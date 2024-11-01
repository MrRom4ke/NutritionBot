# backend/services/message_service.py

from datetime import datetime

from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.message_repository import create_message, update_message_status_as_processed
from services.entity_service import extract_entities
from services.topic_service import find_or_create_topic
from schemas.message_schema import MessageCreate, MessageSchema
from models.message_models import MessageModel
from repositories.entity_repository import save_entity, update_entity_theme_id
from services.user_service import UserService


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_message(self, message_data: dict, tg_user_id: int):
        print('Создание транзакции')
        async with self.db.begin():  # Используем одну транзакцию для всех операций
        # Логика создания и обработки сообщения
            user_service = UserService(self.db)
            print('User service - ', user_service)
            user = await user_service.get_user_by_tg_id(tg_user_id)
            if not user:
                raise ValueError(f"User with ID {tg_user_id} not found.")

            message_create = MessageCreate(
                user_id=user.id,
                text=message_data.get("text"),
                timestamp=datetime.fromtimestamp(message_data.get("timestamp"))
            )
            print("Подготовленое к сохранению сообщение", message_create)
            try:
                saved_message = await create_message(self.db, message_create)
                print("Сохраненное сообщение", saved_message)
            except Exception as e:
                print("Ошибка при сохранении сообщения:", e)
            entity_data = extract_entities(saved_message.text)
            print('СУЩНОСТИ', entity_data)
            await save_entity(self.db, saved_message.id, entity_data)

            # Поиск или создание темы, возможно с запросом к GPT
            await self.handle_topic(entity_data, saved_message.id)

    async def handle_topic(self, entity_data: dict, message_id: UUID):
        """Процесс поиска или создания темы, включая запрос к GPT, если тема не найдена."""
        action = entity_data.get("action")
        object_ = entity_data.get("object")
        topic = await find_or_create_topic(action, object_, message_id, self.db)

        # Обновление идентификатора темы в сущности
        theme_id = topic.id if topic else 0
        await update_entity_theme_id(self.db, message_id, theme_id=theme_id)

        # Обновление состояния сообщения, если GPT использовался
        if topic is None:
            await update_message_status_as_processed(self.db, message_id)
