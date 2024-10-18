from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class BotMessageBase(BaseModel):
    """Базовая схема для модели BotMessage, которая содержит все общие поля."""
    step_number: Optional[int] = None
    text: str
    media_url: Optional[HttpUrl] = None  # Используем HttpUrl для проверки корректности URL

class BotMessageCreate(BotMessageBase):
    """Схема для создания нового BotMessage. Она наследует поля из BotMessageBase."""
    pass

class BotMessage(BotMessageBase):
    """Схема, которая включает все поля модели BotMessage, включая id, и устанавливает orm_mode в True."""
    id: UUID

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    """
    Базовая схема для модели Message, которая содержит все общие поля.
    """
    user_id: UUID
    text: str
    topic: Optional[str] = None
    timestamp: datetime = datetime.now()
    is_processed: bool = False
    token_usage: Optional[int] = None

class MessageCreate(MessageBase):
    """Схема для создания нового сообщения."""
    user_id: UUID
    text: str

class MessageUpdate(MessageBase):
    """Схема для обновления сообщения с уточнением."""
    clarification_text: str

class MessageResponse(BaseModel):
    """
    Схема для ответа после анализа или уточнения сообщения.
    """
    clarification_questions: str


class MessageSchema(MessageBase):
    """Схема, которая включает все поля модели Message, включая id, и устанавливает orm_mode в True."""
    id: UUID

    class Config:
        from_attributes = True
