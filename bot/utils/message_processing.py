import whisper
import os
from typing import Optional
from aiogram import types
from setup.config import logger

# Директория для сохранения голосовых сообщений
DOWNLOAD_DIR = "voice_temps/"

# Убедимся, что директория существует
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def process_message_type(message: types.Message) -> Optional[str]:
    """Обрабатывает текстовые и голосовые сообщения и возвращает их текстовое содержимое."""
    if message.content_type == 'text':
        message_text = message.text
    elif message.content_type == 'voice':
        message_text = await handle_voice_message(message)
    else:
        return None
    if message_text is None:
        return None
    if not await is_valid_length(message, message_text):
        return None
    return message_text

async def is_valid_length(message: types.Message, text: str) -> bool:
    """Проверяет, соответствует ли длина сообщения ограничениям."""
    if len(text) > 220:
        await message.reply(f"Ваше сообщение слишком длинное, пожалуйста, перезапишите")
        return False
    return True


async def handle_voice_message(message: types.Message) -> Optional[str]:
    """Обработка голосового сообщения, скачивание и транскрибирование."""
    try:
        file = await message.bot.get_file(message.voice.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, f"{file.file_id}.ogg")
        await message.bot.download_file(file.file_path, file_path)
        model = whisper.load_model("tiny")
        result = model.transcribe(file_path)
        os.remove(file_path)
        return result['text']
    except Exception as e:
        logger.error(f"Ошибка при обработке голосового сообщения: {str(e)}", exc_info=True)