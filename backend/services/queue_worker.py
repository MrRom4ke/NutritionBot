from fastapi import Depends

from db.session import get_async_session
from utils.queue_manager import fetch_and_clear_user_queue
from utils.redis_client import redis_client
from services.message_service import MessageService
from sqlalchemy.ext.asyncio import AsyncSession


async def process_user_queue(tg_user_id: int, db: AsyncSession):
    """Извлекает сообщения пользователя из очереди и обрабатывает их"""
    message_service = MessageService(db)
    messages = await fetch_and_clear_user_queue(tg_user_id)
    print('Fetched messages:', messages)
    for message_data in messages:
        print('Processing message:', message_data)
        await message_service.process_message(
            message_data=message_data,
            tg_user_id=tg_user_id
        )

async def check_expired_queues(db: AsyncSession = Depends(get_async_session)):
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
                await process_user_queue(tg_user_id, db)
