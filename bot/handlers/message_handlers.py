import asyncio

from aiogram import types
from aiogram.client.session import aiohttp

from config import BACKEND_URL


async def handle_user_message(message: types.Message):
    telegram_id = message.from_user.id
    message_text = message.text

    # Отправляем GET запрос для получения user_id
    endpoint = f"{BACKEND_URL}/api/v1/users/{telegram_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as response:
            if response.status != 200:
                await message.reply("Пользователь не найден.")
                return
            user_data = await response.json()
            user_id = user_data['id']

        # После получения user_id, отправляем POST запрос для анализа сообщения
        analyze_endpoint = f"{BACKEND_URL}/api/v1/messages/analyze-message"
        async with session.post(analyze_endpoint, json={'user_id': user_id, 'text': message_text}) as analyze_response:
            if analyze_response.status != 200:
                await message.reply("Произошла ошибка при анализе сообщения.")
                return
            response_data = await analyze_response.json()
            await message.reply(f"Результат анализа: {response_data['clarification_questions']}")

