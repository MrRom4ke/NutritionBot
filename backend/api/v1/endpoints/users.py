from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from schemas.user_schema import UserCreate, UserSchema
from services.user_service import UserService
from db.session import get_async_session

router = APIRouter()

# +
@router.post("/", response_model=UserSchema)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    user_service = UserService(db)
    # Проверка существования пользователя
    existing_user = await user_service.get_user_by_tg_id(user_data.telegram_id)

    if existing_user:
        # Возвращаем пустой ответ со статусом 204 (No Content), чтобы избежать ошибки
        return Response(status_code=204)
    try:
        return await user_service.create_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{telegram_id}", response_model=UserSchema)
async def read_user(telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    user_service = UserService(db)
    user = await user_service.get_user_by_tg_id(telegram_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserSchema])
async def read_users(db: AsyncSession = Depends(get_async_session)):
    user_service = UserService(db)
    return await user_service.get_all_users()