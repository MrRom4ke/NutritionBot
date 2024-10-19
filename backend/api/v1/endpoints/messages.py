import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from schemas.message_schema import MessageCreate, MessageSchema, MessageUpdate, MessageResponse, MessageProcessResponse, \
    MessageNew, MessageDelete
from services.message_service import MessageService
from db.session import get_async_session
from services.user_service import UserService
from utils.ai_utils import analyze_text

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)


@router.post("/messages/", response_model=MessageSchema)
async def create_message(message_data: MessageCreate, db: AsyncSession = Depends(get_async_session)):
    message_service = MessageService(db)
    message = await message_service.create_message(message_data)
    return message


@router.get("/messages/user/{user_id}", response_model=List[MessageSchema])
async def read_messages_by_user(user_id: UUID, db: AsyncSession = Depends(get_async_session)):
    message_service = MessageService(db)
    messages = await message_service.get_messages_by_user(user_id)
    return messages


@router.get("/messages/{message_id}", response_model=MessageSchema)
async def read_message(message_id: UUID, db: AsyncSession = Depends(get_async_session )):
    message_service = MessageService(db)
    message = await message_service.get_message(message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

#-----------
@router.post('/process', response_model=MessageProcessResponse)
async def process_message(message_new: MessageNew, db: AsyncSession = Depends(get_async_session)):
    try:
        user_service = UserService(db)
        message_service = MessageService(db)

        # Получаем id пользователя
        user = await user_service.get_user_by_tg_id(telegram_id=message_new.telegram_id)
        user_id = user.id
        # Получаем промт из базы данных
        prompt = await message_service.get_prompt('default_prompt')
        # Обработка текста с использованием модели для определения уточняющих вопросов
        clarify_questions, token_usage = await analyze_text(message_new.text, prompt)
        # Сохраняем исходное сообщение в БД
        message = await message_service.create_message(
            MessageCreate(user_id=user_id, text=message_new.text, token_usage=token_usage)
        )

        return MessageProcessResponse(clarify_questions = clarify_questions, message_id = message.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# +
@router.put('/{message_id}', response_model=MessageSchema)
async def update_message_value(message_data: MessageUpdate, db: AsyncSession = Depends(get_async_session)):
    try:
        message_service = MessageService(db)
        # Вызов метода обновления значения
        result = await message_service.update_value(message_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete('/{message_id}', response_model=dict)
async def delete_message(message_id: UUID, db: AsyncSession = Depends(get_async_session)):
    """Удаляет сообщение по идентификатору (UUID)."""
    message_service = MessageService(db)
    try:
        result = await message_service.delete_message(message_id)
        return {"status": "success", "message": result}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        # Логирование ошибки и возврат ответа с ошибкой
        raise HTTPException(status_code=500, detail="Ошибка при удалении сообщения")

#-----------

@router.post("/analyze-message", response_model=MessageResponse)
async def analyze_message(message_data: MessageCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Анализирует входящее сообщение и определяет уточняющие вопросы.

    :param message_data: Данные входящего сообщения.
    :param db: Сессия базы данных.
    :return: Ответ, содержащий уточняющие вопросы.
    """
    message_service = MessageService(db)
    try:
        # Обработка сообщения с использованием AI модели для определения уточняющих вопросов
        response_data = await message_service.analyze_message(message_data)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/clarify-message/{message_id}", response_model=MessageSchema)
async def clarify_message(message_id: int, update_data: MessageUpdate, db: AsyncSession = Depends(get_async_session)):
    """
    Уточняет сообщение с дополнительной информацией.

    :param message_id: ID сообщения для уточнения.
    :param update_data: Данные для уточнения.
    :param db: Сессия базы данных.
    :return: Обновленный ответ, содержащий темы.
    """
    message_service = MessageService(db)
    try:
        # Обновление сообщения после получения уточняющего ответа
        response_data = await message_service.clarify_message(message_id, update_data)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
