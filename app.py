from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import engine, get_db, Base
from models import Provider, ProductKey
from router_logic import estimate_response_complexity
from providers import call_llm, verify_provider_credentials
from template import DASHBOARD_HTML

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Powerful AI Router", version="2.0")

class ProviderVerifyRequest(BaseModel):
    name: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model_name: str

class ProductKeyCreateRequest(BaseModel):
    company_name: str
    low_provider_id: int
    medium_provider_id: int
    hard_provider_id: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML

@app.post("/admin/providers/verify-and-add")
async def verify_and_add_provider(data: ProviderVerifyRequest, db: Session = Depends(get_db)):
    is_valid = await verify_provider_credentials(data.api_key, data.base_url, data.model_name)
    if not is_valid:
        return {"valid": False, "message": "Credentials check failed"}

    provider = Provider(
        name=data.name,
        api_key=data.api_key,
        base_url=data.base_url,
        model_name=data.model_name
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"valid": True, "provider_id": provider.id}

@app.get("/admin/providers")
def list_providers(db: Session = Depends(get_db)):
    return db.query(Provider).filter(Provider.is_active == True).all()

@app.post("/admin/product-key")
def create_product_key(data: ProductKeyCreateRequest, db: Session = Depends(get_db)):
    key = ProductKey.generate_key()
    product = ProductKey(
        key=key,
        name=f"{data.company_name} Product Key",
        company_name=data.company_name,
        low_provider_id=data.low_provider_id,
        medium_provider_id=data.medium_provider_id,
        hard_provider_id=data.hard_provider_id,
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"product_key": product.key}

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Production Key")

    product_key_str = authorization.replace("Bearer ", "").strip()
    product = db.query(ProductKey).filter(
        ProductKey.key == product_key_str,
        ProductKey.is_active == True
    ).first()

    if not product:
        raise HTTPException(401, "Invalid Production Key")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # 1. अंदाज़ा लगाना (Routing Decision)
    complexity = estimate_response_complexity(messages)

    # 2. कंपनी की प्रोडक्शन की में चुनी गई API Key चुनना
    if complexity == "hard":
        provider = product.hard_provider
    elif complexity == "medium":
        provider = provider = product.medium_provider
    else:
        provider = product.low_provider

    if not provider:
        raise HTTPException(500, "Mapped API key not found")

    # 3. चुनी हुई API Key पर सवाल भेजना
    try:
        reply = await call_llm(provider, messages)
    except Exception as e:
        raise HTTPException(500, f"Model Error: {str(e)}")

    return {
        "id": "router-response",
        "object": "chat.completion",
        "model": provider.model_name,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply},
            "finish_reason": "stop"
        }],
        "routed_to": f"{complexity.upper()} -> {provider.name} ({provider.model_name})"
}
    
