# backend/app/main.py

from fastapi import FastAPI

from api.v1.endpoints import users, messages
from db.session import engine, Base


app = FastAPI(title="Nutric Bot Backend")

# Подключение роутеров
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])


# Создание таблиц
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
