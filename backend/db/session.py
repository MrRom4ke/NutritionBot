from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings


# Создание движка
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Асинхронный session maker
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Получаем асинхронную сессию
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session