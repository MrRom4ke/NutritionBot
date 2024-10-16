import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Index, ForeignKey, Table, UniqueConstraint, func

from db.base import Base


class BotMessageModel(Base):
    __tablename__ = 'bot_messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    step_number = Column(Integer, nullable=True, unique=True)  # Номер шага
    text = Column(String, nullable=False)  # Текст сообщения
    media_url = Column(String, nullable=True)  # Ссылка на картинку/видео (если есть)

class MessageModel(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)  # Внешний ключ на таблицу пользователей
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

    # Связь с моделью User
    user = relationship("User", back_populates="messages")