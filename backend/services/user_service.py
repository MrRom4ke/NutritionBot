from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_models import UserModel
from schemas.user_schema import UserCreate, UserSchema


class UserService:
    """Содержит методы для создания пользователей, получения пользователя по ID и получения всех пользователей."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> UserSchema:
        # Создаем объект пользователя из схемы UserCreate
        user = UserModel(**user_data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        # Возвращаем объект схемы UserSchema, чтобы вернуть валидированные данные
        result = UserSchema.from_orm(user)
        return result

    async def get_user(self, user_id: UUID) -> UserSchema:
        # Находим пользователя по ID
        result = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            # Возвращаем объект схемы UserSchema
            return UserSchema.model_validate(user)
        return None  # Можно обработать случай, когда пользователь не найден

    async def get_all_users(self) -> List[UserSchema]:
        # Получаем всех пользователей
        result = await self.db.execute(select(UserModel))
        users = result.scalars().all()
        # Преобразуем список пользователей в список схем для возвращения
        return [UserSchema.model_validate(user) for user in users]
