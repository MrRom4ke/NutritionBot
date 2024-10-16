from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.message_models import MessageModel
from schemas.message_schema import MessageCreate, MessageSchema


class MessageService:
    """Содержит методы для создания сообщений, получения сообщений по ID пользователя и получения сообщения по ID."""

    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message_data: MessageCreate) -> MessageSchema:
        """Создаёт новое сообщение и сохраняет его в базе данных."""
        message = MessageModel(**message_data.dict())
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return MessageSchema.from_orm(message)

    def get_messages_by_user(self, user_id: UUID) -> List[MessageSchema]:
        """Получает все сообщения пользователя по его ID."""
        messages = self.db.query(MessageModel).filter(MessageModel.user_id == user_id).all()
        return [MessageSchema.from_orm(msg) for msg in messages]

    def get_message(self, message_id: UUID) -> Optional[MessageSchema]:
        """Получает конкретное сообщение по его ID."""
        message = self.db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if message:
            return MessageSchema.from_orm(message)
        return None  # Можно обработать этот случай в маршрутах
