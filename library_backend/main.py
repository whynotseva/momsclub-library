"""
LibriMomsClub Backend API
Точка входа приложения
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api import auth, materials, categories, favorites, admin, websocket, activity


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
app.include_router(websocket.router)  # WebSocket без префикса


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    print("🚀 Запуск LibriMomsClub API...")
    print(f"📊 База данных: {settings.DATABASE_URL}")
    print(f"🔐 DEBUG режим: {settings.DEBUG}")
    
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
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )
