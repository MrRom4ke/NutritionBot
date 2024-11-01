# backend/repositories/entity_repository.py

from sqlalchemy import UUID, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.entity_models import EntityModel


async def save_entity(db: AsyncSession, message_id: UUID, entities_data: dict):
    """
    Сохраняет сущность в базе данных, связывая её с сообщением по message_id.

    :param db: Сессия базы данных для асинхронных операций
    :param message_id: UUID сообщения, к которому относится сущность
    :param entities_data: Словарь с данными о сущности (действие, объект, количество, тема)
    :return: Сохраненная сущность
    """
    # Проверка содержимого entities_data
    print(f"Message ID: {message_id}")
    print(f"Entities Data: {entities_data}")

    action = entities_data.get("action")
    object_ = entities_data.get("object")
    quantity = entities_data.get("quantity")

    if not action and not object_ and not quantity:
        print("No valid entity data to save. Exiting save_entity.")
        return None

    try:
        # Создаем запись сущности
        entity = EntityModel(
            message_id=message_id,
            action=action,
            object=object_,
            quantity=quantity,
        )
        db.add(entity)

        # Сохраняем изменения
        await db.commit()
        await db.refresh(entity)
        print(f"Entity saved successfully: {entity}")
        return entity
    except Exception as e:
        # Если произошла ошибка, выводим сообщение об ошибке
        print(f"Failed to save entity: {e}")
        await db.rollback()
        return None


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
    await db.commit()