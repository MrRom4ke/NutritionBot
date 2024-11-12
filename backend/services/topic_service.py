from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.entity_repository import update_entity_theme_id
from repositories.message_repository import update_message_status_as_processed
from repositories.topic_repository import find_or_create_topic


async def handle_topic(entity_data: dict, message_id: UUID, db: AsyncSession,):
    """Процесс поиска или создания темы, включая запрос к GPT, если тема не найдена."""
    action = entity_data.get("action")
    object_ = entity_data.get("object")
    topic = await find_or_create_topic(action, object_, message_id, db)

    # Обновление идентификатора темы в сущности
    theme_id = topic.id if topic else 0
    await update_entity_theme_id(db, message_id, theme_id=theme_id)

    # Обновление состояния сообщения, если GPT использовался
    if topic is None:
        await update_message_status_as_processed(db, message_id)