# handlers/message_handlers.py

import asyncio
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from setup.config import logger
from fsm.states import MessageStates
from utils.api_client import api_client
from utils.message_processing import process_message_type


async def process_message(message: types.Message):
    """Обрабатывает сообщение от пользователя и отправляет его в очередь в Redis на бэкенд."""
    try:
        # Отправляем сообщение на бэкенд
        endpoint = "/api/v1/messages/add_to_queue"
        data = {
            'tg_user_id': message.from_user.id,
            'message_id': message.message_id,
            'text': message.text,
            'timestamp': message.date.timestamp(),
        }
        response_data = await api_client.post(endpoint, data=data)

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения на бэкенд: {str(e)}", exc_info=True)
        await message.reply("Что-то пошло не так. Пожалуйста, попробуйте позже.")


# async def process_message(message: types.Message, state: FSMContext):
#     """Обрабатывает входящее сообщение и взаимодействует с бэкендом для анализа."""
#     telegram_id = message.from_user.id
#     message_text = await process_message_type(message)
#
#     if not message_text:
#         return
#
#     # Проверка текущего состояния: идет ли обработка предыдущего сообщения
#     state_data = await state.get_data()
#     if state_data.get('is_processing'):
#         # Если обработка уже идет, добавляем сообщение в очередь
#         message_queue = state_data.get('message_queue', deque())
#         message_queue.append(message)
#         await state.update_data(message_queue=message_queue)
#         return
#
#     # Устанавливаем флаг, что началась обработка сообщения
#     await state.update_data(is_processing=True)
#
#     try:
#         # Отправляем сообщение на бэкенд для анализа
#         endpoint = f"/api/v1/messages/analyze"
#         response_data = await api_client.post(endpoint, data={'telegram_id': telegram_id, 'text': message_text})
#
#         # Если тема не относится к списку тем
#         if isinstance(response_data, dict) and response_data.get('topic') == 'False':
#             await message.reply("Тема не относится к нашему формату, отправьте, пожалуйста, что-то связанное с едой, активностью и т.д.")
#             return
#
#         # Если сообщение завершено, благодарим пользователя
#         if isinstance(response_data, dict) and response_data.get('is_complete'):
#             await message.reply("Спасибо, ваше сообщение принято.")
#             await state.clear()  # Очищаем состояние
#             return
#
#         # Если нужны уточнения, отправляем уточняющий вопрос и запускаем таймер
#         if isinstance(response_data, dict) and not response_data.get('is_complete'):
#             await message.reply(response_data['clarify_questions'])
#             await state.set_state(MessageStates.waiting_for_details)
#
#             # Запуск таймера на 20 секунд для уточнений
#             timer_task = asyncio.create_task(
#                 process_confirmation_with_timer(telegram_id, message_text, message.bot, state)
#             )
#             await state.update_data(confirmation_timer=timer_task, first_msg_id=response_data['id'])
#
#     except Exception as e:
#         logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
#         await message.reply("Что-то пошло не так. Пожалуйста, попробуйте позже.")
#
#     finally:
#         # После завершения обработки снимаем флаг и проверяем, есть ли сообщения в очереди
#         state_data = await state.get_data()
#         message_queue = state_data.get('message_queue', deque())
#         if message_queue:
#             next_message = message_queue.popleft()
#             await state.update_data(message_queue=message_queue)
#             # Вызываем обработку следующего сообщения
#             await process_message(next_message, state)
#         else:
#             # Очищаем состояние, если очередь пуста
#             await state.clear()


async def process_details(message: types.Message, state: FSMContext):
    """Обрабатывает уточняющие вопросы и отправляет обновление на бэкенд."""
    user_data = await state.get_data()
    first_message_id = user_data.get('first_msg_id')
    confirmation_response = await process_message_type(message)

    if not confirmation_response:
        return

    try:
        # Отправляем уточняющие данные на бэкенд
        endpoint = f"/api/v1/messages/{first_message_id}"
        await api_client.update(
            endpoint=endpoint,
            data={'id': first_message_id, 'text': confirmation_response, 'is_complete': True},
            method='put'
        )

        # Останавливаем таймер и благодарим за уточнение
        state_data = await state.get_data()
        timer_task = state_data.get('confirmation_timer')
        if timer_task:
            timer_task.cancel()

        await message.reply("Спасибо за уточнение, информация обновлена.")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения в API: {str(e)}", exc_info=True)
        await message.reply("Что-то пошло не так. Пожалуйста, попробуйте позже.")


async def process_confirmation_with_timer(user_id, original_message, bot: Bot, state: FSMContext):
    """Запускает таймер ожидания ответа для уточнений."""
    try:
        await asyncio.sleep(20)  # Ждем 20 секунд
        state_data = await state.get_data()

        if 'confirmation_response' not in state_data:
            await bot.send_message(user_id, "Мы не получили от вас уточнение. Пожалуйста, отправьте сообщение снова.")
            first_message_id = state_data.get('first_msg_id')

            try:
                # Удаляем сообщение на бэкенде по его ID
                endpoint = f"/api/v1/messages/{first_message_id}"
                await api_client.delete(endpoint)

            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения в API: {str(e)}", exc_info=True)

        await state.clear()

    except asyncio.CancelledError:
        pass
