# backend/repositories/entity_repository.py
from typing import Optional, Dict

from sqlalchemy import UUID, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from models.entity_models import EntityModel, EntityRequirement


async def save_entity(db: AsyncSession, message_id: UUID, entity_data: dict, entity_requirements_id: int):
    """
    Сохраняет сущность в базе данных, связывая её с сообщением по message_id.

    :param entity_requirements_id:
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
            date=entity_data.get("date"),
            entity_requirements_id=entity_requirements_id,
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

async def find_or_create_entity_requirement(action: str, object_: str, db: AsyncSession) -> EntityRequirement:
    # Проверяем, существует ли такая пара action-object в EntityRequirement
    query = select(EntityRequirement).where(EntityRequirement.action == action, EntityRequirement.object == object_)
    result = await db.execute(query)
    requirement = result.scalar_one_or_none()

    if not requirement:
        # Если пары нет, создаем новую запись
        requirement = EntityRequirement(action=action, object=object_, required_fields=[])
        db.add(requirement)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            # Если запись уже существует, повторно выполняем запрос
            result = await db.execute(query)
            requirement = result.scalar_one_or_none()

    return requirement

async def check_missing_data_and_ask_questions(message_id: UUID, db: AsyncSession) -> Optional[Dict[str, str]]:
    """
    Проверяет наличие обязательных данных в EntityModel для указанного сообщения и возвращает вопросы для недостающих полей.

    Args:
        message_id (UUID): Идентификатор сообщения.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        Optional[Dict[str, str]]: Словарь вопросов для недостающих полей, где ключ - поле, а значение - текст вопроса.
                                   Возвращает None, если вопросы не требуются.
    """
    # Извлечение связанной сущности на основе message_id
    result = await db.execute(select(EntityModel).where(EntityModel.message_id == message_id))
    entity = result.scalars().first()
    print('Entity - ', entity)
    if not entity:
        print(f"Сущность с message_id {message_id} не найдена.")
        return None

    # Получаем связанное требование для action и object сущности
    result = await db.execute(
        select(EntityRequirement).where(
        EntityRequirement.action == entity.action,
            EntityRequirement.object == entity.object
        )
    )
    requirement = result.scalars().first()
    print('Requirement - ', requirement)
    if not requirement:
        print(f"Требования для action '{entity.action}' и object '{entity.object}' не найдены.")
        return None

    # Проверяем значение required_fields перед определением недостающих полей
    print("Required fields in requirement:", requirement.required_fields)
    # Определяем недостающие обязательные поля
    missing_fields = [field for field in requirement.required_fields if getattr(entity, field) is None]
    print('MISSING FIELDS = ', missing_fields)

    # Формируем вопросы для недостающих полей
    questions = {field: requirement.questions[field] for field in missing_fields if field in requirement.questions}
    print('QUESTIONS - ', questions)

    return questions if questions else None