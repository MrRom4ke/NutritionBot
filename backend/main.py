# backend/app/main.py
import asyncio
import os
import sys

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_session

from api.v1.endpoints import users, messages, indicators
from db.session import engine, get_async_session
from db.base import Base

# Импорт всех моделей
from models.user_models import UserModel
from models.indicators_models import IndicatorModel, IndicatorCollectionModel, DailyIndicatorModel
from models.message_models import MessageModel
from services.queue_worker import check_expired_queues
from utils.redis_client import redis_client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Nutric Bot Backend")

# Подключение роутеров
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(indicators.router, prefix="/api/v1/indicators", tags=["indicators"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])


@app.on_event("startup")
async def startup_event():
    # Создание всех таблиц в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Получаем асинхронную сессию
    async for async_session in get_async_session():
        # Создаем фоновую задачу для обработки очередей
        asyncio.create_task(check_expired_queues(async_session))
        break  # Прерываем после получения одной сессии

@app.on_event("shutdown")
async def shutdown_event():
    # Закрытие соединения с базой данных
    await engine.dispose()
    await redis_client.close()


# Настройте маршрут для проверки работы
@app.get("/")
async def read_root():
    return {"message": "API is running"}