# backend/app/core/config.py
import os
import logging
from dotenv import load_dotenv
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    DEBUG: bool = False
    OPENAI_API_CHAT_KEY: Optional[str] = None
    REDIS_URL: str

    class Config:
        env_file = ".env"

load_dotenv()
settings = Settings()

# Настройка логгера
logging.basicConfig(
    level=logging.ERROR,  # Уровень логирования (можно использовать INFO, DEBUG и др.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='core/backend_errors.log',  # Файл для записи логов
    filemode='a'  # Режим добавления в файл (append)
)

logger = logging.getLogger(__name__)