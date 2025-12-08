"""
Подключение к базе данных и сессии
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

from app.config import settings

# Создаём движок БД
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # Логировать SQL запросы в режиме отладки
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base для моделей (если не импортируется из бота)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии БД в FastAPI endpoints
    
    Использование:
        @app.get("/materials")
        def get_materials(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация БД: создание всех таблиц
    Вызывается при старте приложения
    """
    from app.models import library_models
    
    # Создаём все таблицы, если их нет
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")
