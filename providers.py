import httpx
import asyncio
from typing import List, Dict

from MODEL import is_model_supported
from URL import is_url_supported


async def verify_provider_credentials(api_key: str, base_url: str, model_name: str) -> bool:
    """
    Live credentials check system.
    Sahi URL, API Key aur Model ko instantly verify karta hai.
    """
    clean_url = base_url.strip().rstrip('/')
    clean_model = model_name.strip()
    clean_key = api_key.strip()

    # 1. URL Support Check
    if not is_url_supported(clean_url):
        print(f"Validation Failed: '{clean_url}' is not supported in URL.py")
        return False

    # 2. Model Support Check
    if not is_model_supported(clean_model):
        print(f"Validation Failed: '{clean_model}' is not supported in MODEL.py")
        return False

    # 3. Endpoint Path Formatting
    if clean_url.endswith("/chat/completions"):
        full_url = clean_url
    else:
        full_url = f"{clean_url}/chat/completions"

    # Universal Headers: Google Gemini, OpenAI, Claude, DeepSeek, Groq sabhi ke liye
    headers = {
        "Authorization": f"Bearer {clean_key}",
        "x-goog-api-key": clean_key,
        "api-key": clean_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": clean_model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.post(full_url, headers=headers, json=payload)
            return response.status_code == 200
    except Exception as e:
        print(f"Live Verification Error: {str(e)}")
        return False


async def call_llm(provider, messages: List[Dict]) -> str:
    """
    LLM Chat API call handler.
    Auto-retry ke saath high stability deta hai.
    """
    clean_url = provider.base_url.strip().rstrip('/')
    clean_key = provider.api_key.strip()
    
    if clean_url.endswith("/chat/completions"):
        full_url = clean_url
    else:
        full_url = f"{clean_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {clean_key}",
        "x-goog-api-key": clean_key,
        "api-key": clean_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": provider.model_name.strip(),
        "messages": messages,
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        last_error = None
        for attempt in range(3):
            try:
                response = await client.post(full_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                last_error = e
                if attempt < 2:
                    await asyncio.sleep(1.5)
        raise last_error
    
