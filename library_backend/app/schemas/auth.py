"""
Pydantic схемы для авторизации
"""

from typing import Optional
from pydantic import BaseModel, Field


class TelegramAuthData(BaseModel):
    """Данные от Telegram Login Widget"""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class UserInfo(BaseModel):
    """Информация о пользователе"""
    telegram_id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    loyalty_level: str = "none"
    admin_group: Optional[str] = None  # creator, developer, curator
    has_active_subscription: bool
    subscription_end: Optional[str] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class SubscriptionStatus(BaseModel):
    """Статус подписки"""
    has_active_subscription: bool
    subscription_end: Optional[str] = None
    days_left: Optional[int] = None
