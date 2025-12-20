"""
Push Notifications API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Text, text
from sqlalchemy.sql import func
from pywebpush import webpush, WebPushException
import json
import os

from app.database import get_db, Base, engine
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/push", tags=["push"])

VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
VAPID_EMAIL = os.getenv('VAPID_EMAIL', 'mailto:admin@librarymomsclub.ru')


class PushSubscription(Base):
    __tablename__ = 'push_subscriptions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # telegram_id
    endpoint = Column(String, nullable=False, unique=True)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())


class LibraryNotification(Base):
    __tablename__ = 'library_notifications'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # internal user_id (NOT telegram_id!)
    type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    text = Column(Text)
    link = Column(Text)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)


try:
    PushSubscription.__table__.create(engine, checkfirst=True)
except:
    pass


@router.post("/subscribe")
def subscribe_to_push(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    subscription = data.get('subscription')
    if not subscription:
        raise HTTPException(status_code=400, detail="Subscription data required")
    
    endpoint = subscription.get('endpoint')
    keys = subscription.get('keys', {})
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')
    
    if not all([endpoint, p256dh, auth]):
        raise HTTPException(status_code=400, detail="Invalid subscription data")
    
    telegram_id = current_user['telegram_id']
    
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
    
    if existing:
        existing.user_id = telegram_id
        existing.p256dh = p256dh
        existing.auth = auth
    else:
        new_sub = PushSubscription(
            user_id=telegram_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth
        )
        db.add(new_sub)
    
    db.commit()
    return {"success": True, "message": "Subscribed"}


@router.post("/unsubscribe")
def unsubscribe_from_push(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    endpoint = data.get('endpoint')
    if not endpoint:
        raise HTTPException(status_code=400, detail="Endpoint required")
    
    db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).delete()
    db.commit()
    return {"success": True}


def send_push_notification_sync(db: Session, title: str, body: str, url: str = "/library", create_in_app: bool = True):
    """Отправить Push + создать in-app уведомление"""
    if not VAPID_PRIVATE_KEY:
        return 0
    
    subscriptions = db.query(PushSubscription).all()
    
    # Собираем telegram_id подписчиков
    telegram_ids = set()
    
    sent_count = 0
    failed_endpoints = []
    
    for sub in subscriptions:
        telegram_ids.add(sub.user_id)  # это telegram_id
        
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
        }
        
        payload = json.dumps({
            "title": title,
            "body": body,
            "url": url,
            "icon": "/icons/icon-192.png"
        })
        
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL}
            )
            sent_count += 1
        except WebPushException as e:
            if e.response and e.response.status_code in [404, 410]:
                failed_endpoints.append(sub.endpoint)
    
    if failed_endpoints:
        for ep in failed_endpoints:
            db.query(PushSubscription).filter(PushSubscription.endpoint == ep).delete()
        db.commit()
    
    # Создаём in-app уведомления (конвертируем telegram_id -> user_id)
    if create_in_app and telegram_ids:
        for tg_id in telegram_ids:
            # Находим внутренний user_id по telegram_id
            user = db.query(User).filter(User.telegram_id == tg_id).first()
            if user:
                notification = LibraryNotification(
                    user_id=user.id,  # внутренний ID!
                    type="push",
                    title=title,
                    text=body,
                    link=url,
                    is_read=0
                )
                db.add(notification)
        db.commit()
    
    return sent_count


@router.post("/test")
def test_push(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user['telegram_id'] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    sent = send_push_notification_sync(db, "🔔 Тест", "Push работает!", "/library", create_in_app=False)
    return {"success": True, "sent_count": sent}


@router.post("/notify")
def send_notification(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user['telegram_id'] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    title = data.get('title', '🔔 Новый материал')
    body = data.get('body', 'В библиотеке появился новый материал!')
    url = data.get('url', '/library')
    
    sent = send_push_notification_sync(db, title, body, url, create_in_app=True)
    return {"success": True, "sent_count": sent}


@router.get("/subscribers")
def get_push_subscribers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    subs = db.query(PushSubscription.user_id).distinct().all()
    return {"subscribers": [s[0] for s in subs]}


@router.get("/users-stats")
def get_users_with_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    push_subs = db.query(PushSubscription.user_id).distinct().all()
    push_ids = {s[0] for s in push_subs}
    result = db.execute(text("""
        SELECT u.id, u.telegram_id, u.first_name, u.username, u.photo_url,
               COUNT(DISTINCT v.id) as views_count,
               COUNT(DISTINCT f.id) as favorites_count,
               MAX(v.viewed_at) as last_activity
        FROM users u
        LEFT JOIN library_views v ON v.user_id = u.id
        LEFT JOIN library_favorites f ON f.user_id = u.id
        GROUP BY u.id
        HAVING views_count > 0 OR favorites_count > 0
        ORDER BY last_activity DESC NULLS LAST
    """))
    users = []
    for row in result:
        users.append({
            "id": row[0], "telegram_id": row[1], "first_name": row[2],
            "username": row[3], "photo_url": row[4], "views_count": row[5] or 0,
            "favorites_count": row[6] or 0, "last_activity": row[7],
            "has_push": row[1] in push_ids
        })
    return {"users": users, "total": len(users), "with_push": len([u for u in users if u["has_push"]])}


@router.post("/send-broadcast")
def send_push_broadcast(
    title: str,
    body: str,
    url: str = "/library",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отправить Push всем подписчикам"""
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    from app.api.push import send_push_notification_sync
    sent = send_push_notification_sync(db, title, body, url, create_in_app=True)
    return {"success": True, "sent_count": sent}


@router.post("/send-to-user")
def send_push_to_user(
    telegram_id: int,
    title: str,
    body: str,
    url: str = "/library",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отправить Push конкретному пользователю (на все устройства)"""
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    subs = db.query(PushSubscription).filter(PushSubscription.user_id == telegram_id).all()
    if not subs:
        raise HTTPException(status_code=404, detail="Пользователь не подписан на Push")
    
    payload = json.dumps({"title": title, "body": body, "url": url, "icon": "/icons/icon-192.png"})
    sent = 0
    failed_endpoints = []
    
    for sub in subs:
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
        }
        try:
            webpush(subscription_info=subscription_info, data=payload, vapid_private_key=VAPID_PRIVATE_KEY, vapid_claims={"sub": VAPID_EMAIL})
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in [404, 410]:
                failed_endpoints.append(sub.endpoint)
    
    for ep in failed_endpoints:
        db.query(PushSubscription).filter(PushSubscription.endpoint == ep).delete()
    if failed_endpoints:
        db.commit()
    
    return {"success": True, "sent_to": telegram_id, "devices": sent}


@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Аналитика просмотров"""
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Просмотры по дням (последние 7 дней)
    views_by_day = db.execute(text("""
        SELECT DATE(viewed_at) as day, COUNT(*) as count
        FROM library_views
        WHERE viewed_at >= DATE('now', '-7 days')
        GROUP BY DATE(viewed_at)
        ORDER BY day
    """)).fetchall()
    
    # Топ-5 материалов за неделю
    top_materials = db.execute(text("""
        SELECT m.id, m.title, COUNT(v.id) as views
        FROM library_materials m
        LEFT JOIN library_views v ON v.material_id = m.id AND v.viewed_at >= DATE('now', '-7 days')
        GROUP BY m.id
        ORDER BY views DESC
        LIMIT 5
    """)).fetchall()
    
    # Среднее время просмотра (если есть duration_seconds)
    avg_duration = db.execute(text("""
        SELECT AVG(duration_seconds) FROM library_views WHERE duration_seconds > 0
    """)).scalar() or 0
    
    return {
        "views_by_day": [{"day": str(r[0]), "count": r[1]} for r in views_by_day],
        "top_materials": [{"id": r[0], "title": r[1], "views": r[2]} for r in top_materials],
        "avg_duration_seconds": round(avg_duration)
    }


@router.get("/user-details/{telegram_id}")
def get_user_details(
    telegram_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Детали пользователя для модалки"""
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    user = db.execute(text("SELECT id, telegram_id, first_name, username, photo_url FROM users WHERE telegram_id = :tid"), {"tid": telegram_id}).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Просмотры
    views = db.execute(text("""
        SELECT m.title, v.viewed_at FROM library_views v
        JOIN library_materials m ON m.id = v.material_id
        WHERE v.user_id = :uid ORDER BY v.viewed_at DESC LIMIT 10
    """), {"uid": user[0]}).fetchall()
    
    # Избранное
    favorites = db.execute(text("""
        SELECT m.title FROM library_favorites f
        JOIN library_materials m ON m.id = f.material_id
        WHERE f.user_id = :uid
    """), {"uid": user[0]}).fetchall()
    
    # Подписка (из основной БД momsclub)
    subscription = db.execute(text("""
        SELECT end_date FROM subscriptions WHERE user_id = :uid ORDER BY end_date DESC LIMIT 1
    """), {"uid": user[0]}).fetchone()
    
    # Push подписка
    has_push = db.query(PushSubscription).filter(PushSubscription.user_id == telegram_id).first() is not None
    
    return {
        "user": {"id": user[0], "telegram_id": user[1], "first_name": user[2], "username": user[3], "photo_url": user[4]},
        "views": [{"title": v[0], "viewed_at": str(v[1])} for v in views],
        "favorites": [f[0] for f in favorites],
        "subscription_end": str(subscription[0]) if subscription else None,
        "has_push": has_push
    }


@router.post("/force-logout/{telegram_id}")
def force_logout_user(
    telegram_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Разлогинить пользователя (инвалидировать токен)"""
    if current_user["telegram_id"] not in [534740911, 44054166]:
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = db.execute(text("UPDATE users SET token_version = COALESCE(token_version, 1) + 1 WHERE telegram_id = :tid"), {"tid": telegram_id})
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {"success": True, "message": "Пользователь разлогинен"}
