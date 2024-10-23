from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.message_models import MessageModel, PromptModel
from schemas.message_schema import MessageCreate, MessageSchema, MessageUpdate, MessageNewFromTelegram
from utils.ai_utils import analyze_text


class MessageService:
    """Содержит методы сообщений отражающие бизнес логику"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message(self, message_data: MessageCreate) -> MessageSchema:
        """Создаёт новое сообщение и сохраняет его в базе данных."""
        message = MessageModel(**message_data.model_dump())
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return MessageSchema.model_validate(message)

    async def update_message_value(self, message_data: MessageUpdate) -> MessageSchema:
        """Метод для обновления сообщения: добавляет новое значение к существующему полю."""
        result = await self.db.execute(select(MessageModel).where(MessageModel.id == message_data.id))
        message = result.scalar_one_or_none()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        if message_data.text is not None:
            message.text += f'\n{message_data.text}'
        if message_data.token_usage is not None:
            message.token_usage = (message.token_usage or 0) + message_data.token_usage
        if message_data.is_processed is not None:
            message.is_processed = message_data.is_processed
        if message_data.is_complete is not None:
            message.is_complete = message_data.is_complete
        await self.db.commit()
        await self.db.refresh(message)
        return MessageSchema.model_validate(message)

    async def replace_message_value(self, message_data: MessageUpdate) -> MessageSchema:
        """Метод для замены значений сообщения: полностью заменяет существующее значение новым."""
        result = await self.db.execute(select(MessageModel).where(MessageModel.id == message_data.id))
        message = result.scalar_one_or_none()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        if message_data.text is not None:
            message.text = message_data.text
        if message_data.token_usage is not None:
            message.token_usage = message_data.token_usage
        if message_data.is_processed is not None:
            message.is_processed = message_data.is_processed
        if message_data.is_complete is not None:
            message.is_complete = message_data.is_complete
        await self.db.commit()
        await self.db.refresh(message)
        return MessageSchema.model_validate(message)

    async def delete_message(self, message_id: UUID) -> dict:
        """Удаляет сообщение из базы данных по его идентификатору."""
        result = await self.db.execute(select(MessageModel).where(MessageModel.id == message_id))
        message = result.scalar_one_or_none()
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        await self.db.delete(message)
        await self.db.commit()
        return {"status": "success", "message": f"Message with ID {message_id} deleted"}

    async def process_message(self, message_data: MessageNewFromTelegram, user_id: UUID) -> dict:
        """Обработка сообщения пользователя"""
        # 1. Получаем тему
        topic_prompt = await self.get_prompt('topic_prompt')
        topic, token_usage = await analyze_text(f'Text:{message_data.text}\n{topic_prompt}')

        # 2. Сохраняем исходное сообщение
        message = await self.create_message(
            MessageCreate(user_id=user_id, text=message_data.text, topic=topic, token_usage=token_usage)
        )
        if topic == 'False':
            # 2.1 Заканчиваем обработку ставим статус is_processed - True
            await self.update_message_value(MessageUpdate(id=message.id, is_processed=True))
            return {"message_id": message.id, "text":message_data.text, "topic": topic}

        # 3. Определяем суть сообщения, обновляем потраченные токены
        essence_prompt = await self.get_prompt('essence_prompt')
        essence, token_usage = await analyze_text(f'Text:{message_data.text}\n{essence_prompt}')
        await self.replace_message_value(MessageUpdate(id=message.id, text=essence))
        await self.update_message_value(MessageUpdate(id=message.id, token_usage=token_usage))

        # 4. Проверяем полноту сообщения
        is_complete_prompt = await self.get_prompt('is_complete_prompt')
        is_complete, token_usage = await analyze_text(f'Text:{essence}\n{is_complete_prompt}')
        await self.update_message_value(MessageUpdate(id=message.id, is_complete=is_complete, token_usage=token_usage))

        if is_complete == 'True':
            return {"message_id": message.id, "text":essence, "topic": topic, "is_complete": True}

        # 5. Если требуется уточнение, формируем вопрос
        clarify_prompt = await self.get_prompt('clarify_prompt')
        clarify_questions, token_usage = await analyze_text(f'Text:{essence}\n{clarify_prompt}')
        await self.update_message_value(MessageUpdate(id=message.id, token_usage=token_usage))

        return {
            "message_id": message.id,
            "text": essence,
            "topic": topic,
            "is_complete": False,
            "clarify_questions": clarify_questions
        }

    async def get_prompt(self, name: str) -> str:
        prompt_result = await self.db.execute(select(PromptModel).where(PromptModel.name == name))
        prompt = prompt_result.scalars().first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Промт не найден")
        return prompt.content
