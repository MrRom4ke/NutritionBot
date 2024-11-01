# backend/services/entity_service.py

import spacy
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from repositories.entity_repository import save_entity

# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

# Списки временных и количественных единиц
time_units = {"час", "минута", "секунда", "день", "неделя", "месяц", "год"}
quantity_units = {"тарелка", "пачка", "кусок"}


def extract_entities(text: str) -> dict:
    """Извлекает действие, объект и количество из текста."""
    doc = nlp(text)
    action = None
    object_ = None
    quantity = None
    potential_object = None  # Временное хранение объекта, если количество идет после него

    for i, token in enumerate(doc):
        # Определение действия (глагол)
        if token.pos_ == "VERB" and not action:
            action = token.lemma_

        # Проверка количества перед существительным (например, "кусок пиццы")
        if token.lemma_ in quantity_units:
            next_token = doc[i + 1] if i + 1 < len(doc) else None
            prev_token = doc[i - 1] if i > 0 else None

            # "кусок пиццы" или "тарелка борща"
            if next_token and next_token.pos_ == "NOUN":
                object_ = next_token.lemma_
                quantity = token.lemma_
            # "пиццы кусок"
            elif prev_token and prev_token.pos_ == "NOUN":
                object_ = prev_token.lemma_
                quantity = token.lemma_

        # Обработка числового количества с единицей измерения (например, "1 час" или "5 минут")
        elif token.pos_ == "NUM" and not quantity:
            next_token = doc[i + 1] if i + 1 < len(doc) else None
            if next_token and (next_token.lemma_ in quantity_units | time_units):
                quantity = f"{token.text} {next_token.lemma_}"
            else:
                quantity = token.text

        # Определение объекта действия, если он еще не определен
        elif token.pos_ == "NOUN" and not object_:
            if token.lemma_ not in time_units | quantity_units:
                potential_object = token.lemma_
            object_ = object_ or potential_object

    return {"action": action, "object": object_, "quantity": quantity}
