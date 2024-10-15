from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

# Определение модели сообщения
class Message(BaseModel):
    id: int
    content: str

# Создание экземпляра маршрутизатора
router = APIRouter()

# Имитация базы данных для хранения сообщений
messages_db = []

# Получение всех сообщений
@router.get("/", response_model=List[Message])
async def get_messages():
    return messages_db

# Получение сообщения по ID
@router.get("/{message_id}", response_model=Message)
async def get_message(message_id: int):
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=404, detail="Message not found")

# Создание нового сообщения
@router.post("/", response_model=Message)
async def create_message(message: Message):
    messages_db.append(message)
    return message

# Обновление сообщения
@router.put("/{message_id}", response_model=Message)
async def update_message(message_id: int, updated_message: Message):
    for index, message in enumerate(messages_db):
        if message.id == message_id:
            messages_db[index] = updated_message
            return updated_message
    raise HTTPException(status_code=404, detail="Message not found")

# Удаление сообщения
@router.delete("/{message_id}", response_model=Message)
async def delete_message(message_id: int):
    for index, message in enumerate(messages_db):
        if message.id == message_id:
            return messages_db.pop(index)
    raise HTTPException(status_code=404, detail="Message not found")