import asyncio
from nntplib import NNTPDataError

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from config import logger
from states import MessageStates
from api_client import api_client
from utils.message_processing import process_message_type


async def process_message(message: types.Message, state: FSMContext):
    """Метод для входящего сообщения от пользователя."""
    telegram_id = message.from_user.id
    message_text = await process_message_type(message)
    if message_text is None:
        return
    try:
        endpoint = f"/api/v1/messages/process"
        response_data = await api_client.post(endpoint, data={'telegram_id': telegram_id, 'text': message_text})
        await message.reply(response_data['clarify_questions'])
        await state.set_state(MessageStates.waiting_for_details)
        timer_task = asyncio.create_task(process_confirmation_with_timer(telegram_id, message_text, message.bot, state))
        await state.update_data(confirmation_timer=timer_task, first_msg_id=response_data['message_id'])
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
        await message.reply("Что-то пошло не так. Пожалуйста, попробуйте позже.")

async def process_details(message: types.Message, state: FSMContext):
    """Метод для обработки уточняющего ответа от пользователя."""
    user_data = await state.get_data()
    first_message_id = user_data.get('first_msg_id')
    confirmation_response = await process_message_type(message)
    if confirmation_response is None:
        return
    try:
        endpoint = f"/api/v1/messages/{first_message_id}"
        await api_client.update(endpoint, data={'message_id': first_message_id, 'answer_text': confirmation_response}, method='put')
    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения в API: {str(e)}", exc_info=True)
        await message.reply("Что-то пошло не так. Пожалуйста, попробуйте позже.")

    state_data = await state.get_data()
    timer_task = state_data.get('confirmation_timer')
    if timer_task:
        timer_task.cancel()
    await message.reply("Спасибо, добавили")
    await state.clear()

async def process_confirmation_with_timer(user_id, original_message, bot: Bot, state: FSMContext):
    try:
        await asyncio.sleep(300)
        state_data = await state.get_data()
        if 'confirmation_response' not in state_data:
            await bot.send_message(user_id, "Мы не получили от вас уточнения, запишите снова, пожалуйста")
            first_message_id = state_data.get('first_msg_id')
            try:
                endpoint = f"/api/v1/messages/{first_message_id}"
                await api_client.delete(endpoint)
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения в API: {str(e)}", exc_info=True)
                await bot.send_message(user_id, "Ошибка при удалении сообщения, попробуйте позже.")
        await state.clear()

    except asyncio.CancelledError:
        pass
