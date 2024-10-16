from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.message_models import MessageModel
from schemas.message_schema import MessageCreate, MessageSchema


class MessageService:
    """Содержит методы для создания сообщений, получения сообщений по ID пользователя и получения сообщения по ID."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message_data: MessageCreate) -> MessageSchema:
        """Создаёт новое сообщение и сохраняет его в базе данных."""
        message = MessageModel(**message_data.dict())
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return MessageSchema.from_orm(message)

    async def get_messages_by_user(self, user_id: UUID) -> List[MessageSchema]:
        """Получает все сообщения пользователя по его ID."""
        result = await self.db.execute(select(MessageModel).filter(MessageModel.user_id == user_id))
        messages = result.scalars().all()
        return [MessageSchema.from_orm(msg) for msg in messages]

    async def get_message(self, message_id: UUID) -> Optional[MessageSchema]:
        """Получает конкретное сообщение по его ID."""
        result = await self.db.execute(select(MessageModel).filter(MessageModel.id == message_id))
        message = result.scalar_one_or_none()
        if message:
            return MessageSchema.from_orm(message)
        return None  # Можно обработать этот случай в маршрутах
