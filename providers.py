import httpx
from typing import List, Dict

# कैपिटल फाइलों (URL.py और MODEL.py) से फ़ंक्शन इम्पोर्ट करें
from MODEL import is_model_supported
from URL import is_url_supported


async def verify_provider_credentials(api_key: str, base_url: str, model_name: str) -> bool:
    """
    1. चेक करता है कि URL.py में Base URL valid है या नहीं।
    2. चेक करता है कि MODEL.py में Model Name valid है या नहीं।
    3. LLM Endpoint को Live Request भेजकर Test करता है।
    """
    clean_url = base_url.strip().rstrip('/')
    clean_model = model_name.strip()

    # Step 1: Validate URL using URL.py
    if not is_url_supported(clean_url):
        print(f"Validation Failed: '{clean_url}' URL.py में सपोर्टेड नहीं है।")
        return False

    # Step 2: Validate Model using MODEL.py
    if not is_model_supported(clean_model):
        print(f"Validation Failed: '{clean_model}' MODEL.py में सपोर्टेड नहीं है।")
        return False

    # Step 3: Format Completion URL
    if clean_url.endswith("/chat/completions"):
        full_url = clean_url
    else:
        full_url = f"{clean_url}/chat/completions"

    # Step 4: Headers & Test Payload
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": clean_model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }

    # Step 5: Test Live Connection
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(full_url, headers=headers, json=payload)
            return response.status_code == 200
    except Exception as e:
        print(f"Live Verification Error: {str(e)}")
        return False


async def call_llm(provider, messages: List[Dict]) -> str:
    """
    यूज़र के मैसेजेस को असली LLM Provider को भेजता है और रिस्पॉन्स लौटाता है।
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
