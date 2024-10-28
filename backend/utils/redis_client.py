from redis.asyncio import Redis
import os

# Получаем URL для подключения к Redis из переменной окружения
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        """Инициализируем подключение к Redis"""
        if not self.redis:
            try:
                self.redis = await Redis.from_url(REDIS_URL)
            except Exception as e:
                print(f"Ошибка подключения к Redis: {e}")

    async def get_redis(self):
        """Возвращает Redis клиент после подключения"""
        if self.redis is None:
            await self.connect()
        return self.redis

    async def close(self):
        """Закрытие Redis подключения"""
        if self.redis:
            await self.redis.close()

# Создаем экземпляр клиента Redis
redis_client = RedisClient()
