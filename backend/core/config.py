# backend/app/core/config.py
import os
from dotenv import load_dotenv
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    DEBUG: bool = False
    OPENAI_API_CHAT_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

load_dotenv()
settings = Settings()