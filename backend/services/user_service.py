from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from models.user_models import UserModel
from schemas.user_schema import UserCreate, UserSchema


class UserService:
    """Содержит методы для создания пользователей, получения пользователя по ID и получения всех пользователей."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> UserSchema:
        # Создаем объект пользователя из схемы UserCreate
        user = UserModel(**user_data.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        # Возвращаем объект схемы UserSchema, чтобы вернуть валидированные данные
        return UserSchema.from_orm(user)

    def get_user(self, user_id: UUID) -> UserSchema:
        # Находим пользователя по ID
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            # Возвращаем объект схемы UserSchema
            return UserSchema.from_orm(user)
        return None  # Можно обработать случай, когда пользователь не найден

    def get_all_users(self) -> List[UserSchema]:
        # Получаем всех пользователей
        users = self.db.query(UserModel).all()
        # Преобразуем список пользователей в список схем для возвращения
        return [UserSchema.from_orm(user) for user in users]
