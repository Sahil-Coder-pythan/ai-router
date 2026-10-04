import httpx
from typing import List, Dict
from models import Provider
from MODEL import is_model_supported
from URL import is_url_supported

async def verify_provider_credentials(api_key: str, base_url: str, model_name: str) -> bool:
    """
    1. Base URL aur Model name ko validate karta hai.
    2. Endpoint ko Sahi tareeqe se format karta hai (double /chat/completions ko rokta hai).
    3. POST request bhejkar live credentials check karta hai.
    """
    clean_url = base_url.strip().rstrip('/')
    clean_model = model_name.strip()

    # Step 1: Validate URL
    if not is_url_supported(clean_url):
        print(f"Validation Failed: URL '{clean_url}' URL.py mein supported nahi hai.")
        return False

    # Step 2: Validate Model
    if not is_model_supported(clean_model):
        print(f"Validation Failed: Model '{clean_model}' MODEL.py mein supported nahi hai.")
        return False

    # Step 3: Smart Endpoint Formatting
    if clean_url.endswith("/chat/completions"):
        full_url = clean_url
    else:
        full_url = f"{clean_url}/chat/completions"

    # Step 4: Headers and Payload
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": clean_model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    # Step 5: Send POST Request
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(full_url, headers=headers, json=payload)
            return response.status_code == 200
    except Exception as e:
        print(f"Verification Error: {str(e)}")
        return False


async def call_llm(provider: Provider, messages: List[Dict]) -> str:
    """
    LLM ko POST request bhejkar response mangaata hai.
    """
    clean_url = provider.base_url.strip().rstrip('/')
    
    if clean_url.endswith("/chat/completions"):
        full_url = clean_url
    else:
        full_url = f"{clean_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {provider.api_key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": provider.model_name.strip(),
        "messages": messages,
        "temperature": 0.7
    }

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
