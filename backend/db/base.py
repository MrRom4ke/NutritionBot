import asyncio

from sqlalchemy.orm import declarative_base

from db.session import engine


# Базовый класс для моделей
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())