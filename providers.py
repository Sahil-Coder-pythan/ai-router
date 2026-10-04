import httpx
from typing import List, Dict

async def verify_provider_credentials(api_key: str, base_url: str, model_name: str) -> bool:
    """API Key, Model और Base URL सही हैं या नहीं, यह टेस्ट करने के लिए"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload
            )
            return response.status_code == 200
    except Exception:
        return False

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
