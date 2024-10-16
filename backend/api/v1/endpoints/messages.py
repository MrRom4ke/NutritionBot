from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from schemas.message_schema import MessageCreate, MessageSchema
from services.message_service import MessageService
from db.session import async_session

router = APIRouter()

@router.post("/messages/", response_model=MessageSchema)
def create_message(message_data: MessageCreate, db: Session = Depends(async_session)):
    message_service = MessageService(db)
    message = message_service.create_message(message_data)
    return message

@router.get("/messages/user/{user_id}", response_model=List[MessageSchema])
def read_messages_by_user(user_id: UUID, db: Session = Depends(async_session)):
    message_service = MessageService(db)
    messages = message_service.get_messages_by_user(user_id)
    return messages

@router.get("/messages/{message_id}", response_model=MessageSchema)
def read_message(message_id: UUID, db: Session = Depends(async_session)):
    message_service = MessageService(db)
    message = message_service.get_message(message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message