from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.message_models import MessageModel, PromptModel
from schemas.message_schema import MessageCreate, MessageSchema, MessageResponse, MessageUpdate
from utils.ai_utils import analyze_text, finalize_analysis


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
        return MessageSchema.model_validate(message)

    async def analyze_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Анализирует сообщение и генерирует уточняющие вопросы.

        :param message_data: Данные сообщения для анализа.
        :return: Ответ, содержащий уточняющие вопросы.
        """

        # Получаем промт из базы данных
        prompt_result = await self.db.execute(select(PromptModel).where(PromptModel.name == "default_prompt"))
        prompt = prompt_result.scalars().first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Промт не найден")

        # Обработка текста с использованием модели для определения уточняющих вопросов
        response, token_usage = await analyze_text(message_data.text, prompt.content)

        # Сохраняем исходное сообщение
        message = MessageModel(user_id=message_data.user_id, text=message_data.text, token_usage=token_usage)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        print(response)
        print(token_usage)
        return MessageResponse(clarification_questions=response)

    async def clarify_message(self, message_id: int, update_data: MessageUpdate) -> MessageResponse:
        """
        Уточняет сообщение с дополнительной информацией и выполняет финальный анализ.

        :param message_id: ID сообщения для уточнения.
        :param update_data: Данные для уточнения.
        :return: Ответ, содержащий обновленные темы.
        """
        # Обновляем сообщение после получения уточняющего ответа
        result = await self.db.execute(select(MessageModel).where(MessageModel.id == message_id))
        message = result.scalars().first()
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")

        message.text += f" {update_data.clarification_text}"
        await self.db.commit()
        await self.db.refresh(message)

        # Финальная обработка текста после получения уточнения
        themes = finalize_analysis(message.text)
        return MessageResponse(theme=themes, clarification_questions=[])

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
