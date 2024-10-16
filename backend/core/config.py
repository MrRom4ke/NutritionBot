# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings  # Используем pydantic-settings


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()