from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from models.message_models import PromptModel


# ------------------- Базовые схемы входящих сообщений -------------------
class MessageBase(BaseModel):
    """Базовая схема для модели Message."""
    user_id: UUID
    text: str
    timestamp: datetime
    topic: Optional[str] = None
    is_complete: Optional[bool] = None
    is_processed: bool = False
    token_usage: Optional[int] = None

    class Config:
        from_attributes = True  # Чтобы Pydantic мог работать с ORM объектами

class MessageCreate(MessageBase):
    """Схема для создания нового сообщения."""
    pass

class MessageRead(MessageBase):
    """Схема для возврата данных о сообщении (чтение)."""
    id: UUID

    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    """Схема для обновления сообщения"""
    id: UUID
    text: Optional[str] = None
    topic: Optional[str] = None
    is_complete: Optional[bool] = None
    is_processed: Optional[bool] = None
    token_usage: Optional[int] = None

class MessageDelete(BaseModel):
    """Схема для удаления сообщения по его id"""
    id: UUID

class MessageSchema(MessageBase):
    """Схема, которая включает все поля модели Message"""
    id: UUID

    class Config:
        from_attributes = True


# ------------------- Схемы для анализа сообщений -------------------
class MessageQueueInput(BaseModel):
    """Схема для входящего сообщения"""
    tg_user_id: int
    message_id: int
    text: str
    timestamp: float

class MessageNewFromTelegram(BaseModel):
    """Схема для создания нового сообщения из Telegram"""
    telegram_id: int
    text: str

class MessageIsNotTopic(BaseModel):
    id: UUID
    text: str
    topic: str

class MessageIsComplete(BaseModel):
    id: UUID
    text: str
    topic: Optional[str]
    is_complete: bool

class MessageClarify(BaseModel):
    id: UUID
    text: str
    topic: Optional[str]
    is_complete: bool
    clarify_questions: str


# ------------------- Схемы для работы с промтами -------------------
class PromptContent(PromptModel):
    """Схема получения промтов из БД"""


# ------------------- Схема для исходящих от бота сообщений -------------------
