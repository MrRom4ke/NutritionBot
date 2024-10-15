from aiogram import types


# Команда /start
async def start(message: types.Message):
    await message.answer("Добро пожаловать!")