# backend/app/main.py
import os
import sys

from fastapi import FastAPI

from api.v1.endpoints import users, messages, indicators
from db.session import engine
from db.base import Base

# Импорт всех моделей
from models.user_models import UserModel
from models.indicators_models import IndicatorModel, IndicatorCollectionModel, DailyIndicatorModel
from models.message_models import MessageModel


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

@app.on_event("shutdown")
async def shutdown_event():
    # Закрытие соединения с базой данных
    await engine.dispose()

# Используйте Middleware для обработки сессий
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройте маршрут для проверки работы
@app.get("/")
async def read_root():
    return {"message": "API is running"}