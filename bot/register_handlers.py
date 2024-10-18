from aiogram import Dispatcher, F
from aiogram.filters import Command

from handlers.start import start
from handlers.message_handlers import handle_user_message


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=['start']))
    dp.message.register(handle_user_message, F.content_type.in_(['text', 'voice']))
