# bot/config.py
import logging
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

# Настройка логгера
logging.basicConfig(
    level=logging.ERROR,  # Уровень логирования (можно использовать INFO, DEBUG и др.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='utils/bot_errors.log',  # Файл для записи логов
    filemode='a'  # Режим добавления в файл (append)
)

logger = logging.getLogger(__name__)