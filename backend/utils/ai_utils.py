# backend/utils/ai_utils.py
import openai
import asyncio
from core.config import settings


openai.api_key = settings.OPENAI_API_CHAT_KEY

async def analyze_text(text: str, prompt: str):
    """
    Анализирует текст и определяет уточняющие вопросы.

    :param text: Текст для анализа.
    :param prompt: Промт для использования в анализе.
    :return: Список уточняющих вопросов и количество потраченных токенов.
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Сообщение пользователя: {text}\n{prompt}"}
        ],
        max_tokens=50
    )
    response_text = response.choices[0].message.content
    token_usage = response.usage.total_tokens
    return response_text, token_usage

async def finalize_analysis(text: str):
    """
    Финальный анализ текста для разделения на темы.

    :param text: Текст для финального анализа.
    :return: Разделенные темы сообщения.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Разбей текст на темы: {text}"}
        ],
        max_tokens=100
    )
    themes = response['choices'][0]['message']['content']
    return themes
