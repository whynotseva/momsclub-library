"""
LibriMomsClub Backend API
Точка входа приложения
"""

import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# Настраиваем файловое логирование
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "library_backend.log"
ERROR_LOG_FILE = LOG_DIR / "library_backend.error.log"

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5,
    encoding="utf-8",
)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
)
file_handler.setFormatter(formatter)

error_file_handler = RotatingFileHandler(
    ERROR_LOG_FILE,
    maxBytes=2 * 1024 * 1024,  # 2 MB
    backupCount=5,
    encoding="utf-8",
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(error_file_handler)

logger = logging.getLogger("library_backend")

# Пробрасываем логи uvicorn в файл
for uvicorn_logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
    logging.getLogger(uvicorn_logger_name).addHandler(file_handler)

from app.database import init_db
from app.api import auth, materials, categories, favorites, admin, websocket, activity, push



# Создаём приложение FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API для закрытой библиотеки MomsClub",
    docs_url="/docs" if settings.DEBUG else None,  # Swagger UI только в dev режиме
    redoc_url="/redoc" if settings.DEBUG else None,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(materials.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(favorites.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(activity.router, prefix=settings.API_V1_PREFIX)
app.include_router(push.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router)  # WebSocket без префикса


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    print("🚀 Запуск LibriMomsClub API...")
    print(f"📊 База данных: {settings.DATABASE_URL}")
    print(f"🔐 DEBUG режим: {settings.DEBUG}")
    logger.info("API startup: db=%s debug=%s", settings.DATABASE_URL, settings.DEBUG)
    
    # Инициализация БД (создание таблиц, если их нет)
    # init_db()  # Закомментировано, т.к. таблицы уже созданы через миграцию
    
    print("✅ API готов к работе!")


@app.get("/")
def root():
    """Корневой endpoint"""
    return {
        "message": "LibriMomsClub API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production"
    }


@app.get("/health")
def health_check():
    """Проверка здоровья API"""
    return {"status": "ok", "service": "LibriMomsClub API"}


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Обработчик 404 ошибок"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint не найден"}
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Обработчик 500 ошибок"""
    logger.exception("Internal server error: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логируем каждый HTTP запрос"""
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        raise exc

    process_time = (time.time() - start_time) * 1000
    logger.info(
        "HTTP %s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
