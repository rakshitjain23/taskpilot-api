import httpx
from app.core.config import settings

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


async def deepseek_chat(messages: list, max_tokens: int = 512):
    """
    DeepSeek Cloud Chat Completion API Wrapper
    """

    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(DEEPSEEK_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
