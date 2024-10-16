from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from schemas.message_schema import MessageCreate, MessageSchema
from services.message_service import MessageService
from db.session import get_async_session

router = APIRouter()

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
