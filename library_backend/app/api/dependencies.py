"""
Dependencies для FastAPI endpoints
"""

from typing import Optional
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.database import get_db
from app.utils.auth import decode_access_token


# Security scheme для JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    payload = decode_access_token(credentials.credentials)
    telegram_id = payload.get("telegram_id")
    
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    
    result = db.execute(
        text("SELECT id, telegram_id, first_name, username, photo_url, current_loyalty_level, admin_group FROM users WHERE telegram_id = :tg_id"),
        {"tg_id": telegram_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return {
        "user_id": result[0],
        "telegram_id": result[1],
        "first_name": result[2],
        "username": result[3],
        "photo_url": result[4],
        "loyalty_level": result[5] or "none",
        "admin_group": result[6]
    }


def get_current_user_with_subscription(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    print(f"🔍 Checking subscription for user_id={current_user['user_id']}")
    
    result = db.execute(
        text("""
        SELECT 
            s.id,
            s.is_active,
            s.end_date
        FROM subscriptions s
        WHERE s.user_id = :user_id
          AND s.is_active = 1
          AND s.end_date > datetime('now')
        ORDER BY s.end_date DESC
        LIMIT 1
        """),
        {"user_id": current_user["user_id"]}
    ).fetchone()
    
    print(f"🔍 Subscription result: {result}")
    
    if not result:
        print(f"❌ No active subscription for user_id={current_user['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет активной подписки MomsClub"
        )
    
    current_user["subscription"] = {
        "id": result[0],
        "is_active": bool(result[1]),
        "end_date": result[2]
    }
    
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
