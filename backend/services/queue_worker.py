import asyncio

from fastapi import Depends

from db.session import get_async_session
from utils.queue_manager import fetch_and_clear_user_queue
from utils.redis_client import redis_client
from services.message_service import MessageService
from sqlalchemy.ext.asyncio import AsyncSession


async def process_user_queue(tg_user_id: int):
    """Обрабатывает очередь сообщений пользователя с ограничением параллельных задач."""
    messages = await fetch_and_clear_user_queue(tg_user_id)
    print('Fetched messages:', messages)


    # Оборачиваем процесс обработки сообщения в задачу с использованием семафора
    async def process_single_message(message_data):
        # Создаем новую сессию для каждого сообщения
        async for db in get_async_session():
            message_service = MessageService(db)
            await message_service.process_message(message_data, tg_user_id)

    # Запускаем параллельные задачи для каждого сообщения
    tasks = [process_single_message(message) for message in messages]
    await asyncio.gather(*tasks)

async def check_expired_queues():
    """Фоновая задача: проверка истекших очередей и запуск их обработки"""
    redis = await redis_client.get_redis()
    pubsub = redis.pubsub()

    # Подписываемся на канал уведомлений об истечении срока действия ключей
    await pubsub.subscribe("__keyevent@0__:expired")
    async for message in pubsub.listen():
        if message["type"] == "message":
            key = message["data"].decode()
            if key.startswith("user_timer:"):
                tg_user_id = int(key.split(":")[-1])
                await process_user_queue(tg_user_id)
