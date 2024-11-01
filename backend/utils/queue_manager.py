import json

from utils.redis_client import redis_client


async def add_message_to_queue(tg_user_id: int, message_id: int, text: str, timestamp: float):
    """Добавляет сообщение в очередь с таймером истечения"""
    redis = await redis_client.get_redis()
    queue_key = f"user_queue:{tg_user_id}"
    message_data = json.dumps({
        "message_id": message_id,
        "text": text,
        "timestamp": timestamp,
    })
    await redis.rpush(queue_key, message_data)
    await redis.set(f"user_timer:{tg_user_id}", "active", ex=3)


async def fetch_and_clear_user_queue(tg_user_id: int):
    """Извлекает все сообщения из очереди и очищает её"""
    redis = await redis_client.get_redis()
    queue_key = f"user_queue:{tg_user_id}"
    messages = await redis.lrange(queue_key, 0, -1)
    await redis.delete(queue_key)
    result = [json.loads(msg) for msg in messages]
    print('RESULT', result)
    return result