# backend/services/entity_service.py
import re

import spacy
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from repositories.entity_repository import save_entity

# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

# Допустимые единицы измерения для количества и времени
quantity_units = {"кусок", "стакан", "чашка", "порция", "литр", "сигарета"}
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

        # Определение объектов и условий
        if token.pos_ == "NOUN":
            # Проверяем, если перед существительным стоит прилагательное или количество
            prev_token = doc[i - 1] if i > 0 else None
            if prev_token and prev_token.lemma_ in quantity_units:
                entities["quantity"] = prev_token.text  # количество
                entities["object"] = token.lemma_  # объект, который следует за количеством
            elif not entities["object"]:
                entities["object"] = token.lemma_

            # Если перед существительным стоит прилагательное (например, "маленькая чашка")
            if prev_token and prev_token.pos_ == "ADJ":
                entities["specific_object"] = f"{prev_token.lemma_} {token.lemma_}"

        # Определение специфического объекта (например, "кофе без сахара")
        if token.lemma_ in quantity_units:
            next_token = doc[i + 1] if i + 1 < len(doc) else None
            if next_token and next_token.pos_ == "NOUN":
                entities["object"] = next_token.lemma_
                entities["quantity"] = token.text
                if i + 2 < len(doc) and doc[i + 2].lemma_ == "без":
                    entities["specific_object"] = f"{next_token.lemma_} без {doc[i + 3].lemma_}"

        # Извлечение размера (например, "маленькая порция")
        if token.dep_ == "amod" and token.head.pos_ == "NOUN":
            entities["size"] = token.text

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

    return entities
