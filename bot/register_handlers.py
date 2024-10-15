from aiogram.filters import Command

from aiogram import Dispatcher
from handlers.start import start


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=['start']))