# backend/repositories/message_repository.py

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from models.message_models import MessageModel, PromptModel
from schemas.message_schema import MessageUpdate, MessageSchema, MessageCreate


async def get_message_by_id(db: AsyncSession, message_id: UUID) -> MessageModel:
    result = await db.execute(select(MessageModel).where(MessageModel.id == message_id))
    return result.scalar_one_or_none()

async def create_message(db: AsyncSession, message_data: MessageCreate) -> MessageSchema:
    """Создаёт новое сообщение и сохраняет его в базе данных."""
    try:
        message = MessageModel(**message_data.model_dump())
        db.add(message)
        await db.flush()
        await db.refresh(message)
        print("Сообщение успешно сохранено:", message)
        return MessageSchema.model_validate(message)
    except Exception as e:
        print("Ошибка при создании сообщения:", e)
        await db.rollback()  # Откат транзакции в случае ошибки
        raise  # Повторный выброс ошибки для обработки выше по цепочке

async def update_message_token_usage(db: AsyncSession, message_update: MessageUpdate) -> None:
    message = await get_message_by_id(db, message_update.id)
    if message is None:
        raise ValueError("Message not found")
    message.token_usage = (message.token_usage or 0) + (message_update.token_usage or 0)
    await db.flush()
    await db.refresh(message)

async def update_message_status_as_processed(db: AsyncSession, message_id: UUID) -> None:
    """Обновляет статус сообщения как обработанного."""
    await db.execute(
        update(MessageModel)
        .where(MessageModel.id == message_id)
        .values(is_processed=True)
    )
    await db.commit()

async def get_prompt_by_name(db: AsyncSession, name: str) -> str:
    """Получает текст промта из таблицы PromptModel по его имени."""
    result = await db.execute(select(PromptModel).where(PromptModel.name == name))
    prompt = result.scalars().first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Промт не найден")

    return prompt.content
