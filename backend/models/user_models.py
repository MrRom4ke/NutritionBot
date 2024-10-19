import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String,  Boolean,  DateTime

from db.base import Base


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())

    messages = relationship("MessageModel", back_populates="user", cascade="all, delete-orphan")
    collections = relationship('IndicatorCollectionModel', back_populates='user')
    daily_indicators = relationship('DailyIndicatorModel', back_populates='user')