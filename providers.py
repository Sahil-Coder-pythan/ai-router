import httpx
from typing import List, Dict

async def call_llm(provider, messages: List[Dict]) -> str:
    headers = {
        "Authorization": f"Bearer {provider.api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": provider.model_name,
        "messages": messages,
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{provider.base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]