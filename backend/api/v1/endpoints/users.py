from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from schemas.user_schema import UserCreate, UserSchema
from services.user_service import UserService
from db.session import async_session

router = APIRouter()

@router.post("/users/", response_model=UserSchema)
def create_user(user_data: UserCreate, db: Session = Depends(async_session)):
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user

@router.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: UUID, db: Session = Depends(async_session)):
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/", response_model=List[UserSchema])
def read_users(is_active: Optional[bool] = None, db: Session = Depends(async_session)):
    user_service = UserService(db)
    users = user_service.get_all_users(is_active=is_active)
    return users