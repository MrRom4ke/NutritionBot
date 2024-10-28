import spacy
from spacy.tokens import Doc


# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

def extract_entities(text: str) -> dict:
    """Извлекает действие, предмет и количество из текста."""
    doc = nlp(text)
    action = None
    subject = None
    quantity = None

    # Ищем сущности и части речи
    for token in doc:
        # Определение действия (глагол)
        if token.pos_ == "VERB":
            action = token.lemma_  # Основная форма глагола

        # Определение предмета (существительное)
        if token.pos_ == "NOUN" or token.ent_type_ == "OBJECT":
            subject = token.text

        # Определение количества (число + единицы измерения)
        if token.pos_ == "NUM":
            quantity = token.text
            if token.nbor().pos_ in {"NOUN", "SYM"}:  # Количество + предмет (например, "минут")
                quantity += " " + token.nbor().text

    return {
        "action": action,
        "subject": subject,
        "quantity": quantity
    }