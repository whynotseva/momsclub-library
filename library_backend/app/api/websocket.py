"""
WebSocket для отслеживания онлайн пользователей
"""

import json
from typing import Dict, Set
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

from app.config import settings


router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        # Активные соединения по страницам
        # {"library": {user_id: {"ws": WebSocket, "user": {...}}}, "admin": {...}}
        self.active_connections: Dict[str, Dict[int, dict]] = {
            "library": {},
            "admin": {}
        }
    
    async def connect(self, websocket: WebSocket, user_data: dict, page: str):
        """Подключение пользователя"""
        await websocket.accept()
        user_id = user_data["telegram_id"]
        
        print(f"🟢 User {user_data['first_name']} ({user_id}) connected to {page}")
        
        self.active_connections[page][user_id] = {
            "ws": websocket,
            "user": user_data,
            "connected_at": datetime.now().isoformat()
        }
        
        # Рассылаем обновление всем
        await self.broadcast_online_users()
    
    async def disconnect(self, user_id: int, page: str):
        """Отключение пользователя"""
        if user_id in self.active_connections[page]:
            del self.active_connections[page][user_id]
        
        # Рассылаем обновление всем
        await self.broadcast_online_users()
    
    def get_online_users(self) -> dict:
        """Получить список онлайн пользователей"""
        result = {
            "library": [],
            "admin": []
        }
        
        for page in ["library", "admin"]:
            for user_id, data in self.active_connections[page].items():
                result[page].append({
                    "telegram_id": data["user"]["telegram_id"],
                    "first_name": data["user"]["first_name"],
                    "username": data["user"].get("username"),
                    "photo_url": data["user"].get("photo_url"),
                    "admin_group": data["user"].get("admin_group"),
                    "connected_at": data["connected_at"]
                })
        
        return result
    
    async def broadcast_online_users(self):
        """Рассылка списка онлайн пользователей всем подключенным"""
        online_users = self.get_online_users()
        message = json.dumps({
            "type": "online_users",
            "data": online_users,
            "library_count": len(online_users["library"]),
            "admin_count": len(online_users["admin"])
        }, ensure_ascii=False)
        
        print(f"📡 Broadcasting to {len(self.active_connections['library'])} library + {len(self.active_connections['admin'])} admin users")
        
        # Отправляем всем в library и admin
        for page in ["library", "admin"]:
            disconnected = []
            for user_id, data in list(self.active_connections[page].items()):
                try:
                    await data["ws"].send_text(message)
                except Exception as e:
                    print(f"❌ Failed to send to {user_id}: {e}")
                    disconnected.append(user_id)
            
            # Удаляем отключившихся
            for user_id in disconnected:
                if user_id in self.active_connections[page]:
                    del self.active_connections[page][user_id]

    async def broadcast_activity(self, activity_data: dict):
        """Рассылка события активности всем админам"""
        message = json.dumps({
            "type": "new_activity",
            "data": activity_data
        }, ensure_ascii=False)
        
        # Отправляем только админам
        disconnected = []
        for user_id, data in list(self.active_connections["admin"].items()):
            try:
                await data["ws"].send_text(message)
            except Exception as e:
                print(f"❌ Failed to send activity to {user_id}: {e}")
                disconnected.append(user_id)
        
        for user_id in disconnected:
            if user_id in self.active_connections["admin"]:
                del self.active_connections["admin"][user_id]
    
    async def broadcast_admin_action(self, action_data: dict):
        """Рассылка действия админа всем админам"""
        message = json.dumps({
            "type": "admin_action",
            "data": action_data
        }, ensure_ascii=False)
        
        print(f"📡 Broadcasting admin action: {action_data.get('action')} by {action_data.get('admin_name')}")
        
        # Отправляем всем админам
        disconnected = []
        for user_id, data in list(self.active_connections["admin"].items()):
            try:
                await data["ws"].send_text(message)
            except Exception as e:
                print(f"❌ Failed to send admin action to {user_id}: {e}")
                disconnected.append(user_id)
        
        for user_id in disconnected:
            if user_id in self.active_connections["admin"]:
                del self.active_connections["admin"][user_id]


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
async def get_online_users():
    """REST endpoint для получения онлайн пользователей"""
    return manager.get_online_users()
