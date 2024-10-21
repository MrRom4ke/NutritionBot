from aiogram import Dispatcher, F
from aiogram.filters import Command

from handlers.start import start
from handlers.message_handlers import process_message, process_details
from states import MessageStates


def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command(commands=['start']))
    dp.message.register(process_details,MessageStates.waiting_for_details)
    dp.message.register(process_message, F.content_type.in_(['text', 'voice']))
