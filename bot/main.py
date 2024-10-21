# bot/main.py

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from register_handlers import register_handlers
from config import BOT_TOKEN


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
register_handlers(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())