import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from schemas.message_schema import MessageSchema, MessageUpdate, MessageNewFromTelegram,\
    MessageIsComplete, MessageIsNotTopic, MessageClarify
from services.message_service import MessageService
from db.session import get_async_session
from services.user_service import UserService

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

@router.post('/analyze', response_model=Union[MessageIsNotTopic, MessageIsComplete, MessageClarify])
async def analyze_message(message_data: MessageNewFromTelegram, db: AsyncSession = Depends(get_async_session)):
    """Первичный анализ сообщения и отправка уточняющих вопросов при необходимости"""
    try:
        user_service = UserService(db)
        message_service = MessageService(db)

        # Получаем ID пользователя
        user = await user_service.get_user_by_tg_id(telegram_id=message_data.telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Передаем обработку сообщения в сервис
        result = await message_service.process_message(message_data, user.id)

        # Проверяем результат
        print(result)
        if result['topic'] == 'False':
            return MessageIsNotTopic(id=result['message_id'], text=result['text'], topic=result['topic'])
        if result['is_complete']:
            return MessageIsComplete(
                id=result['message_id'],
                text=result['text'],
                topic=result['topic'],
                is_complete=result['is_complete'])
        else:
            return MessageClarify(
                id=result['message_id'],
                text=result['text'],
                topic=result['topic'],
                is_complete=False,
                clarify_questions=result['clarify_questions'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @router.post('/analyze', response_model=MessageSchema)
# async def analyze_message(message_data: MessageNewFromTelegram, db: AsyncSession = Depends(get_async_session)):
#     """Первичный анализ сообщения"""
#     try:
#         user_service = UserService(db)
#         message_service = MessageService(db)
#
#         # Получаем ID пользователя
#         user = await user_service.get_user_by_tg_id(telegram_id=message_new.telegram_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         user_id = user.id
#
#         # Получаем тему
#         topic_prompt = await message_service.get_prompt('topic_prompt')
#         prompt = f'{message_new.text}\n{topic_prompt}'
#         topic, token_usage = await analyze_text(prompt)
#         # Сохраняем исходное сообщение в БД
#         message = await message_service.create_message(
#             MessageCreate(user_id=user_id, text=message_new.text, topic=topic, is_complete=False, token_usage=token_usage)
#         )
#         if topic is 'False':
#             return MessageTopicNotSatisfying(topic=topic)
#
#         # Получаем суть сообщения и обновляем значение в БД
#         essence_prompt = await message_service.get_prompt('essence_prompt')
#         prompt = f'{message_new.text}\n{essence_prompt}'
#         essence, token_usage = await analyze_text(prompt=prompt)
#         await message_service.replace_value(MessageUpdate(message_id=message.id, text=essence))
#         await message_service.update_token_usage(MessageUpdate(message_id=message.id, token_usage=token_usage))
#
#         # Проверяем нужен ли уточняющий вопрос
#         is_complete_prompt = await message_service.get_prompt('is_complete_prompt')
#         prompt = f'{essence}\n{is_complete_prompt}'
#         is_complete, token_usage = await analyze_text(prompt=prompt)
#         await message_service.update_token_usage(MessageUpdate(message_id=message.id, token_usage=token_usage))
#         if is_complete is 'True':
#             return MessageIsComplete(is_complete=bool(is_complete))
#         else:
#             clarify_prompt = await message_service.get_prompt('clarify_prompt')
#             prompt = f'{essence}\n{clarify_prompt}'
#             clarify_question, token_usage = await analyze_text(prompt=prompt)
#             await message_service.update_token_usage(
#                 MessageUpdate(message_id=message.id, token_usage=token_usage)
#             )
#             return MessageAnalyzeResponse(message_id=message.id, topic=topic, is_complete=is_complete, clarify_questions=clarify_question, )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
