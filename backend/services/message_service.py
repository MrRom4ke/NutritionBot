# backend/services/message_service.py

from datetime import datetime
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
        saved_message = await create_message(self.db, message_create)
        print("Сохраненное сообщение", saved_message)
        entity_data = extract_entities(saved_message.text)
        print('СУЩНОСТИ', entity_data)
        print("ID", saved_message.id)
        await save_entity(self.db, saved_message.id, entity_data)

        # Поиск или создание темы
        action = entity_data.get("action")
        object_ = entity_data.get("object")
        topic = await find_or_create_topic(action, object_, saved_message.id, self.db)
        if topic:
            await update_entity_theme_id(self.db, saved_message.id, theme_id=topic.id)
        else:
            await update_entity_theme_id(self.db, saved_message.id, theme_id=0)
            await update_message_status_as_processed(self.db, saved_message.id)
