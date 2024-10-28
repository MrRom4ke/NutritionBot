from aiogram import types
from aiogram.client.session import aiohttp

from setup.config import BACKEND_URL


# Команда /start
async def start(message: types.Message):
    tg_id = message.from_user.id
    user_name = message.from_user.username

    endpoint = f"{BACKEND_URL}/api/v1/users"
    # Отправляем сообщение на FastAPI
    async with aiohttp.ClientSession() as session:
        await session.post(endpoint, json={'telegram_id': tg_id, 'username': user_name})
    await message.answer("Добро пожаловать!")