from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession

from sqlalchemy.orm import sessionmaker

from core.config import settings


# Создание движка
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Создание сессии
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

