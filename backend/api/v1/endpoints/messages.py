import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from schemas.message_schema import MessageCreate, MessageSchema, MessageUpdate, MessageResponse
from services.message_service import MessageService
from db.session import get_async_session

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
