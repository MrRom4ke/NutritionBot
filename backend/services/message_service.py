# backend/services/message_service.py
import json
from datetime import datetime
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.message_repository import create_message
from services.entity_service import extract_entities
from schemas.message_schema import MessageCreate
from repositories.entity_repository import save_entity, find_or_create_entity_requirement, \
    check_missing_data_and_ask_questions
from services.topic_service import handle_topic
from services.user_service import UserService
from utils.redis_client import redis_client


async def accumulate_questions(tg_user_id: int, new_questions: Dict[str, str]):
    """
    Накапливает вопросы для пользователя в Redis, добавляя новые к уже существующим.

    Args:
        tg_user_id (int): Идентификатор пользователя Telegram.
        new_questions (Dict[str, str]): Новые вопросы, которые нужно добавить, где ключ - поле, а значение - текст вопроса.
    """
    redis = await redis_client.get_redis()
    key = f"questions:{tg_user_id}"

    # Загружаем существующие вопросы, если они есть
    existing_questions_json = await redis.get(key)
    if existing_questions_json:
        existing_questions = json.loads(existing_questions_json)
    else:
        existing_questions = {}

    # Объединяем существующие вопросы с новыми
    updated_questions = {**existing_questions, **new_questions}

    # Сохраняем обновленный список вопросов
    updated_questions_json = json.dumps(updated_questions)
    await redis.set(key, updated_questions_json, ex=3600)  # Устанавливаем срок жизни ключа на 1 час



class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_message(self, message_data: dict, tg_user_id: int):
        print('Создание транзакции')
        try:
            async with self.db.begin():  # Используем одну транзакцию для всех операций
                # 1. Получаем пользователя
                user_service = UserService(self.db)
                print('User service - ', user_service)
                user = await user_service.get_user_by_tg_id(tg_user_id)
                if not user:
                    raise ValueError(f"User with ID {tg_user_id} not found.")
                # 2. Сохраняем сообщение
                message_create = MessageCreate(
                    user_id=user.id,
                    text=message_data.get("text"),
                    timestamp=datetime.fromtimestamp(message_data.get("timestamp"))
                )
                print("Подготовленое к сохранению сообщение", message_create)
                try:
                    saved_message = await create_message(self.db, message_create)
                    print("Сохраненное сообщение", saved_message)
                except Exception as e:
                    print("Ошибка при сохранении сообщения:", e)
                # 3. Извлекаем сущности
                entity_data = extract_entities(saved_message.text)
                print('СУЩНОСТИ', entity_data)
                # 4. Проверка или создание требования для action и object
                requirement = await find_or_create_entity_requirement(
                    action=entity_data.get('action'),
                    object_=entity_data.get('object'),
                    db=self.db)
                # 5. Сохранение сущности с привязкой к `entity_requirements_id`
                await save_entity(self.db, saved_message.id, entity_data, entity_requirements_id=requirement.id)
                # 6. Обработка темы
                await handle_topic(entity_data, saved_message.id, self.db)
                # 7. Проверка недостающих данных и накопление вопросов
                questions = await check_missing_data_and_ask_questions(saved_message.id, self.db)
                if questions:
                    # Накапливаем вопросы в Redis для последующей отправки
                    await accumulate_questions(tg_user_id, questions)
        except Exception as e:
            print("Ошибка во время обработки сообщения:", e)
            import traceback
            traceback.print_exc()
            raise  # Повторно выбрасываем исключение для обработки на уровне выше