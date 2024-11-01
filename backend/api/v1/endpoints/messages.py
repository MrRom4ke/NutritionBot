import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from schemas.message_schema import MessageSchema, MessageUpdate, MessageQueueInput
from services.message_service import MessageService
from db.session import get_async_session
from utils.queue_manager import add_message_to_queue


router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

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

