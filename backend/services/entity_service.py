# backend/services/entity_service.py
import re

import spacy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from models.entity_models import EntityModel, EntityRequirement
from repositories.entity_repository import save_entity
from utils.redis_client import redis_client

# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

# Допустимые единицы измерения для количества и времени
quantity_units = {"кусок", "стакан", "чашка", "порция", "литр", "сигарета"}
size_indicators = {"тарелка", "миска", "порция"}  # Возможные слова для размера
time_units = {"минут", "час", "утра", "вечера"}

def extract_entities(text: str) -> dict:
    """Извлекает действие, объект, место, количество и другие параметры из текста."""
    doc = nlp(text)
    entities = {
        "action": None,
        "object": None,
        "specific_object": None,
        "location": None,
        "quantity": None,
        "size": None,
        "conditions": None,
        "duration": None,
        "time": None,
        "date": None,
    }

    for i, token in enumerate(doc):
        # Определение действия (глагол)
        if token.pos_ == "VERB" and not entities["action"]:
            entities["action"] = token.lemma_

        # Проверка размера и объекта
        if token.pos_ == "NOUN":
            prev_token = doc[i - 1] if i > 0 else None
            next_token = doc[i + 1] if i + 1 < len(doc) else None

            # Проверка на наличие размера перед объектом
            if token.lemma_ in size_indicators and not entities["size"]:
                entities["size"] = token.text
                if next_token and next_token.pos_ == "NOUN":
                    entities["object"] = next_token.lemma_

            # Если слово - объект (существительное), но не `size`, сохраняем его
            elif not entities["object"] and token.lemma_ not in size_indicators:
                entities["object"] = token.lemma_

            # Если перед существительным стоит прилагательное (например, "гороховый суп")
            if prev_token and prev_token.pos_ == "ADJ" and not entities["specific_object"]:
                entities["specific_object"] = f"{prev_token.lemma_} {token.lemma_}"

        # Условия с "без" или "с"
        if token.lemma_ in quantity_units:
            next_token = doc[i + 1] if i + 1 < len(doc) else None
            if next_token and next_token.pos_ == "NOUN":
                entities["object"] = next_token.lemma_
                entities["quantity"] = token.text
                if i + 2 < len(doc) and doc[i + 2].lemma_ == "без":
                    entities["specific_object"] = f"{next_token.lemma_} без {doc[i + 3].lemma_}"

        # Извлечение времени или даты через регулярное выражение
        time_match = re.search(r"\b\d{1,2}[:.]\d{2}\b", text)
        if time_match:
            entities["time"] = time_match.group(0)

        # Извлечение продолжительности
        duration_match = re.search(r"\b\d+\s?(минут|час)\b", text)
        if duration_match:
            entities["duration"] = duration_match.group(0)

        # Определение места
        if token.ent_type_ == "LOC" or token.ent_type_ == "GPE":
            entities["location"] = token.text

    # Если `size` найдено, но объект нет, удаляем `size`
    if entities["size"] and not entities["object"]:
        entities["size"] = None

    return entities

async def send_questions_to_user(entity: EntityModel, db: AsyncSession):
    """
    Формирует и отправляет вопросы пользователю, основанные на недостающих полях сущности.
    """
    # 1. Получаем требования к обязательным полям для данной пары action и object
    requirement = await db.execute(
        select(EntityRequirement).where(
            EntityRequirement.action == entity.action,
            EntityRequirement.object == entity.object
        )
    ).scalars().first()

    if not requirement:
        # Логируем случай, когда требования не найдены
        print(f"Требования для action '{entity.action}' и object '{entity.object}' не найдены.")
        return

    # 2. Определяем недостающие поля
    missing_fields = [field for field in requirement.required_fields if getattr(entity, field) is None]

    # 3. Формируем вопросы для недостающих полей
    questions = [
        requirement.questions[field] for field in missing_fields if field in requirement.questions
    ]

    if questions:
        # Собираем все вопросы в одно сообщение
        questions_text = "\n".join(questions)

        # Отправляем одним сообщением через вебхук
        await send_message_via_webhook(entity.message_id, questions_text)  # функция вебхука для отправки сообщения


async def send_message_via_webhook(message_id: UUID, questions_text: str):
    """
    Отправляет сообщение пользователю через вебхук с текстом вопросов.
    """
    import httpx  # Можно разместить импорт наверху файла для повторного использования

    webhook_url = "https://your-webhook-url.com/send"  # Замените на ваш URL вебхука
    payload = {
        "message_id": str(message_id),
        "text": questions_text,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)

    if response.status_code != 200:
        print(f"Ошибка отправки вебхука: {response.status_code} - {response.text}")
