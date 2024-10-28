import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from schemas.message_schema import MessageSchema, MessageUpdate, MessageNewFromTelegram, \
    MessageIsComplete, MessageIsNotTopic, MessageClarify, MessageQueueInput
from services.message_service import MessageService
from db.session import get_async_session
from services.user_service import UserService
from utils.queue_manager import add_message_to_queue

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)


@router.put('/{message_id}', response_model=MessageSchema)
async def update_message_value(message_data: MessageUpdate, db: AsyncSession = Depends(get_async_session)):
    """Обновляет сообщение по идентификатору (UUID)."""
    try:
        message_service = MessageService(db)
        result = await message_service.update_message_value(message_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete('/{message_id}', response_model=dict)
async def delete_message(message_id: UUID, db: AsyncSession = Depends(get_async_session)):
    """Удаляет сообщение по идентификатору (UUID)."""
    try:
        message_service = MessageService(db)
        result = await message_service.delete_message(message_id)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# @router.post("/add_to_queue")
# async def add_message_to_queue(message_data: MessageQueueInput, db: AsyncSession = Depends(get_async_session)):
#     """Добавляет сообщение в очередь для пользователя и запускает/перезапускает таймер."""
#     try:
#         # Создаем менеджер очереди для пользователя
#         queue_manager = MessageQueueManager(redis_client, message_data.telegram_id)
#
#         # Добавляем сообщение в очередь
#         await queue_manager.add_message({
#             'text': message_data.text
#         })
#
#         return {"status": "Message added to queue"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.post("/process_queue")
# async def process_user_queue(telegram_id: int):
#     """
#     Обрабатывает очередь сообщений для указанного пользователя после завершения таймера.
#     """
#     try:
#         # Создаем менеджер очереди для пользователя
#         queue_manager = MessageQueueManager(redis_client, telegram_id)
#
#         # Обрабатываем очередь сообщений
#         await queue_manager.process_queue()
#
#         return {"status": "Queue processed"}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_to_queue")
async def add_message_to_queue_route(message: MessageQueueInput):
    """Добавляет сообщение пользователя в очередь"""
    try:
        await add_message_to_queue(
            tg_user_id=message.tg_user_id,
            message_id=message.message_id,
            text=message.text,
            timestamp=message.timestamp,
        )
        return {"status": "success", "detail": "Message added to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post('/analyze', response_model=Union[MessageIsNotTopic, MessageIsComplete, MessageClarify])
# async def analyze_message(message_data: MessageQueueInput, db: AsyncSession = Depends(get_async_session)):
#     """Первичный анализ сообщения и отправка уточняющих вопросов при необходимости"""
#     try:
#         user_service = UserService(db)
#         message_service = MessageService(db)
#
#         # Получаем ID пользователя
#         user = await user_service.get_user_by_tg_id(telegram_id=message_data.telegram_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#
#         # Передаем обработку сообщения в сервис
#         result = await message_service.process_message(message_data, user.id)
#
#         # Проверяем результат
#         print(result)
#         if result['topic'] == 'False':
#             return MessageIsNotTopic(id=result['message_id'], text=result['text'], topic=result['topic'])
#         if result['is_complete']:
#             return MessageIsComplete(
#                 id=result['message_id'],
#                 text=result['text'],
#                 topic=result['topic'],
#                 is_complete=result['is_complete'])
#         else:
#             return MessageClarify(
#                 id=result['message_id'],
#                 text=result['text'],
#                 topic=result['topic'],
#                 is_complete=False,
#                 clarify_questions=result['clarify_questions'])
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
