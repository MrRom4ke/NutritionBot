from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional


class UserBase(BaseModel):
    """Базовая схема, содержащая общие поля для пользователя. Используется для создания и обновления данных."""
    telegram_id: int
    username: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())

class UserCreate(UserBase):
    """Схема для создания нового пользователя. Она наследует поля из UserBase,
    так как в этом случае поля id и created_at будут установлены автоматически."""


class UserUpdate(UserBase):
    """Схема для обновления существующего пользователя. Все поля, кроме id, являются опциональными,
    чтобы можно было обновить только те поля, которые необходимо изменить."""
    username: Optional[str] = None
    is_active: Optional[bool] = None

class UserSchema(UserBase):
    """Схема, которая включает все поля модели User, включая id, и также устанавливает orm_mode в True,
    чтобы можно было использовать объекты SQLAlchemy при возврате ответов."""
    id: UUID

    class Config:
        from_attributes = True