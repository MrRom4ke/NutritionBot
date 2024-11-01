# backend/utils/ai_utils.py
import openai
import asyncio
from core.config import settings


openai.api_key = settings.OPENAI_API_CHAT_KEY

async def analyze_text(prompt: str):
    """Анализирует текст и выдает результат по промту и количество потраченных токенов"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"{prompt}"}
        ],
        max_tokens=50
    )
    response_text = response.choices[0].message.content
    token_usage = response.usage.total_tokens
    return response_text, token_usage
