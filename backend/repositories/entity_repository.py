# backend/repositories/entity_repository.py

from sqlalchemy import UUID, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.entity_models import EntityModel


async def save_entity(db: AsyncSession, message_id: UUID, entity_data: dict):
    """
    Сохраняет сущность в базе данных, связывая её с сообщением по message_id.

    :param db: Сессия базы данных для асинхронных операций
    :param message_id: UUID сообщения, к которому относится сущность
    :param entity_data: Словарь с данными о сущности (действие, объект, количество, ..., тема)
    :return: Сохраненная сущность
    """
    try:
        entity = EntityModel(
            message_id=message_id,
            action=entity_data.get("action"),
            object=entity_data.get("object"),
            specific_object=entity_data.get("specific_object"),
            location=entity_data.get("location"),
            quantity=entity_data.get("quantity"),
            size=entity_data.get("size"),
            conditions=entity_data.get("conditions"),
            duration=entity_data.get("duration"),
            time=entity_data.get("time"),
            date=entity_data.get("date")
        )
        db.add(entity)
        await db.flush()  # Сохраняем изменения в рамках транзакции, но без коммита
        print("Сущность успешно сохранена:", entity)
    except Exception as e:
        print("Ошибка при сохранении сущности:", e)
        await db.rollback()  # Откат в случае ошибки
        raise

async def update_entity_theme_id(db: AsyncSession, message_id: UUID, theme_id: int) -> None:
    """
    Обновляет поле theme_id для записи в таблице Entity.

    :param db: Сессия базы данных для асинхронных операций
    :param message_id: UUID сообщения, к которому относится сущность
    :param theme_id: Идентификатор темы, если существует, иначе 0 для обозначения нерелевантной темы
    """
    await db.execute(
        update(EntityModel)
        .where(EntityModel.message_id == message_id)
        .values(theme_id=theme_id)
    )
    await db.flush()