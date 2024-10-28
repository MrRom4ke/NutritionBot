from aiogram.fsm.state import StatesGroup, State


class MessageStates(StatesGroup):
    waiting_for_details = State()   # Ожидание ответа на уточняющий вопрос