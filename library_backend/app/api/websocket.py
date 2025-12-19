"""
WebSocket для отслеживания онлайн пользователей
С Redis pub/sub для синхронизации между workers
"""

import json
import asyncio
import os
from typing import Dict
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
import redis.asyncio as redis

from app.config import settings


router = APIRouter(tags=["WebSocket"])

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis ключи
REDIS_ONLINE_USERS_KEY = "presence:online_users"
REDIS_CHANNEL = "presence:broadcast"


class ConnectionManager:
    """Менеджер WebSocket соединений с Redis для синхронизации между workers"""
    
    def __init__(self):
        # Локальные WebSocket соединения этого worker'а
        self.local_connections: Dict[str, Dict[int, WebSocket]] = {
            "library": {},
            "admin": {}
        }
        self.redis: redis.Redis = None
        self.pubsub = None
        self._listener_task = None
    
    async def init_redis(self):
        """Инициализация Redis соединения"""
        if not self.redis:
            self.redis = redis.from_url(REDIS_URL, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(REDIS_CHANNEL)
            # Запускаем слушатель в фоне
            self._listener_task = asyncio.create_task(self._listen_redis())
            print(f"🔴 Redis connected for WebSocket presence")
    
    async def _listen_redis(self):
        """Слушаем Redis канал для получения обновлений от других workers"""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self._handle_redis_message(message["data"])
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Redis listener error: {e}")
    
    async def _handle_redis_message(self, data: str):
        """Обработка сообщения из Redis — рассылаем всем локальным соединениям"""
        # Рассылаем всем локальным WebSocket соединениям
        for page in ["library", "admin"]:
            disconnected = []
            for user_id, ws in list(self.local_connections[page].items()):
                try:
                    await ws.send_text(data)
                except Exception:
                    disconnected.append(user_id)
            
            for user_id in disconnected:
                if user_id in self.local_connections[page]:
                    del self.local_connections[page][user_id]
    
    async def connect(self, websocket: WebSocket, user_data: dict, page: str):
        """Подключение пользователя"""
        await self.init_redis()
        await websocket.accept()
        user_id = user_data["telegram_id"]
        
        print(f"🟢 User {user_data['first_name']} ({user_id}) connected to {page}")
        
        # Сохраняем локальное соединение
        self.local_connections[page][user_id] = websocket
        
        # Сохраняем в Redis (глобальное состояние)
        user_key = f"{page}:{user_id}"
        user_info = {
            "telegram_id": user_data["telegram_id"],
            "first_name": user_data["first_name"],
            "username": user_data.get("username"),
            "photo_url": user_data.get("photo_url"),
            "admin_group": user_data.get("admin_group"),
            "connected_at": datetime.now().isoformat()
        }
        await self.redis.hset(REDIS_ONLINE_USERS_KEY, user_key, json.dumps(user_info, ensure_ascii=False))
        
        # Рассылаем обновление всем через Redis
        await self.broadcast_online_users()
    
    async def disconnect(self, user_id: int, page: str):
        """Отключение пользователя"""
        # Удаляем локальное соединение
        if user_id in self.local_connections[page]:
            del self.local_connections[page][user_id]
        
        # Удаляем из Redis
        if self.redis:
            user_key = f"{page}:{user_id}"
            await self.redis.hdel(REDIS_ONLINE_USERS_KEY, user_key)
        
        # Рассылаем обновление всем
        await self.broadcast_online_users()
    
    async def get_online_users(self) -> dict:
        """Получить список онлайн пользователей из Redis"""
        result = {"library": [], "admin": []}
        
        if not self.redis:
            return result
        
        all_users = await self.redis.hgetall(REDIS_ONLINE_USERS_KEY)
        
        for key, value in all_users.items():
            page = key.split(":")[0]
            if page in result:
                try:
                    user_data = json.loads(value)
                    result[page].append(user_data)
                except json.JSONDecodeError:
                    pass
        
        return result
    
    async def broadcast_online_users(self):
        """Рассылка списка онлайн пользователей через Redis pub/sub"""
        if not self.redis:
            return
        
        online_users = await self.get_online_users()
        message = json.dumps({
            "type": "online_users",
            "data": online_users,
            "library_count": len(online_users["library"]),
            "admin_count": len(online_users["admin"])
        }, ensure_ascii=False)
        
        print(f"📡 Broadcasting: {len(online_users['library'])} library + {len(online_users['admin'])} admin users")
        
        # Публикуем в Redis канал — все workers получат это сообщение
        await self.redis.publish(REDIS_CHANNEL, message)

    async def broadcast_activity(self, activity_data: dict):
        """Рассылка события активности через Redis"""
        if not self.redis:
            return
        
        message = json.dumps({
            "type": "new_activity",
            "data": activity_data
        }, ensure_ascii=False)
        
        await self.redis.publish(REDIS_CHANNEL, message)
    
    async def broadcast_admin_action(self, action_data: dict):
        """Рассылка действия админа через Redis"""
        if not self.redis:
            return
        
        message = json.dumps({
            "type": "admin_action",
            "data": action_data
        }, ensure_ascii=False)
        
        print(f"📡 Broadcasting admin action: {action_data.get('action')} by {action_data.get('admin_name')}")
        await self.redis.publish(REDIS_CHANNEL, message)


# Глобальный менеджер
manager = ConnectionManager()


async def broadcast_new_activity(activity: dict):
    """Вызов из других модулей для рассылки активности"""
    await manager.broadcast_activity(activity)


async def broadcast_admin_action(action: dict):
    """Вызов из других модулей для рассылки админских действий"""
    await manager.broadcast_admin_action(action)


def decode_token(token: str) -> dict:
    """Декодировать JWT токен"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


@router.websocket("/ws/presence")
async def websocket_presence(
    websocket: WebSocket,
    token: str = Query(...),
    page: str = Query(default="library")
):
    """
    WebSocket для отслеживания присутствия пользователей
    
    Query params:
    - token: JWT токен
    - page: "library" или "admin"
    """
    # Проверяем токен
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    telegram_id = payload.get("telegram_id")
    if not telegram_id:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Получаем данные пользователя из БД (упрощённо через токен)
    # В реальности нужно запросить из БД
    from app.database import get_db
    from sqlalchemy import text
    
    db = next(get_db())
    result = db.execute(
        text("SELECT telegram_id, first_name, username, photo_url, admin_group FROM users WHERE telegram_id = :tg_id"),
        {"tg_id": telegram_id}
    ).fetchone()
    
    if not result:
        await websocket.close(code=4004, reason="User not found")
        return
    
    user_data = {
        "telegram_id": result[0],
        "first_name": result[1],
        "username": result[2],
        "photo_url": result[3],
        "admin_group": result[4]
    }
    
    # Подключаем
    await manager.connect(websocket, user_data, page)
    
    try:
        while True:
            # Ждём сообщения (ping/pong для поддержания соединения)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        await manager.disconnect(telegram_id, page)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(telegram_id, page)


@router.get("/api/online-users")
async def get_online_users_endpoint():
    """REST endpoint для получения онлайн пользователей"""
    await manager.init_redis()
    return await manager.get_online_users()
