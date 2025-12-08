"""
Утилиты для авторизации и работы с JWT токенами
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings


def verify_telegram_auth(auth_data: Dict[str, Any]) -> bool:
    """
    Проверка подлинности данных от Telegram Login Widget
    
    Args:
        auth_data: Данные от Telegram (id, first_name, hash, auth_date, etc.)
    
    Returns:
        True если данные подлинные, False если нет
    """
    check_hash = auth_data.pop('hash', None)
    if not check_hash:
        print("❌ No hash in auth_data")
        return False
    
    # Фильтруем None значения
    filtered_data = {k: v for k, v in auth_data.items() if v is not None}
    
    # Создаём строку для проверки
    data_check_string = '\n'.join([
        f'{k}={v}' for k, v in sorted(filtered_data.items())
    ])
    
    print(f"📝 Data check string: {data_check_string[:100]}...")
    print(f"🔑 Bot token (first 10): {settings.TELEGRAM_BOT_TOKEN[:10]}...")
    
    # Создаём секретный ключ из bot token
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Вычисляем hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    print(f"🧮 Calculated: {calculated_hash[:20]}...")
    print(f"📨 Received:   {check_hash[:20]}...")
    
    # Сравниваем
    return calculated_hash == check_hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена
    
    Args:
        data: Данные для токена (обычно {'telegram_id': 123456789})
        expires_delta: Время жизни токена
    
    Returns:
        JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Декодирование JWT токена
    
    Args:
        token: JWT токен
    
    Returns:
        Данные из токена
    
    Raises:
        HTTPException: Если токен невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
