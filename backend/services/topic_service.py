# backend/services/topic_service.py

from openai import OpenAIError
from sqlalchemy import select, UUID, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from models.entity_models import Topic, Keyword
from repositories.message_repository import update_message_token_usage, get_prompt_by_name
from schemas.message_schema import MessageUpdate
from utils.ai_utils import analyze_text


async def find_or_create_topic(action: str, object_: str, message_id: UUID, db: AsyncSession) -> Topic | None:
    """Ищет тему по ключевым словам в БД, если не находит, запрашивает у GPT и создает новую."""
    # Убираем None из ключевых слов
    keywords = [kw for kw in [action, object_] if kw]
    # Проверка существующей темы
    results = await db.execute(
        select(Topic)
        .join(Keyword, Keyword.topic_id == Topic.id)
        .where(or_(Keyword.word == action, Keyword.word == object_))
    )
    topics = results.scalars().all()
    print('Topics - ', [t.name for t in topics])
    if topics:
        return topics[0]

    # Если тема не найдена, выполняем запрос к GPT для определения новой темы
    print("Тема не найдена, обращаемся к GPT")
    prompt_text = f"По словам {', '.join(keywords)}. {await get_prompt_by_name(db, 'define_topic')}"
    # Запрос к GPT
    response_text, token_usage = await analyze_text(prompt_text)
    print(f"Ответ от GPT: {response_text}, Потраченные токены: {token_usage}")

    # Обновление токенов в сообщении
    await update_message_token_usage(db, MessageUpdate(id=message_id, token_usage=token_usage))
    print("Обновление токенов в сообщении завершено")

    # Если GPT вернул новую тему, создаем ее или добавляем к существующей
    if response_text != "False":
        topic_name = response_text.strip()
        existing_topic = await db.scalar(select(Topic).where(Topic.name == topic_name))
        if existing_topic:
            print(f"Тема {topic_name} уже существует. Добавляем ключевые слова: {keywords}")
            await add_keywords_to_topic(existing_topic.id, keywords, db)
            return existing_topic
        print(f"Создаем новую тему: {topic_name} с ключевыми словами: {keywords}")
        topic = await create_topic_with_keywords(topic_name, keywords, db)
        print(f"Новая тема добавлена: {topic}")
        return topic
    return None

async def add_keywords_to_topic(topic_id: int, keywords: list[str], db: AsyncSession):
    """Добавляет новые ключевые слова к существующей теме, избегая дубликатов."""
    try:
        # Извлекаем существующие ключевые слова (множество строк)
        result = await db.execute(select(Keyword.word).where(Keyword.topic_id == topic_id))
        existing_keywords = set(result.scalars().all())

        # Фильтруем ключевые слова, которые еще не добавлены
        new_keywords = [Keyword(word=word, topic_id=topic_id) for word in keywords if
                        word and word not in existing_keywords]

        # Если есть новые ключевые слова, добавляем их
        if new_keywords:
            db.add_all(new_keywords)
            await db.flush()  # Сохраняем без коммита
            print(f"Добавлены новые ключевые слова для темы {topic_id}: {[kw.word for kw in new_keywords]}")
        else:
            print("Новых ключевых слов для добавления нет.")

    except Exception as e:
        print("Ошибка при добавлении ключевых слов:", e)
        await db.rollback()  # Откат в случае ошибки
        raise

async def create_topic_with_keywords(topic_name: str, keywords: list[str], db: AsyncSession) -> Topic:
    """Создает новую тему и добавляет к ней указанные ключевые слова."""
    new_topic = Topic(name=topic_name)
    db.add(new_topic)
    await db.flush()
    for word in keywords:
        if word:  # Добавляем только непустые ключевые слова
            keyword = Keyword(word=word, topic_id=new_topic.id)
            db.add(keyword)
    await db.commit()
    print(f"Создана новая тема: {new_topic.name} с ключевыми словами: {keywords}")
    return new_topic

