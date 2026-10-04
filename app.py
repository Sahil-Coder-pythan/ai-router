from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os

from database import engine, get_db, Base
from models import Provider, ProductKey
from router_logic import get_cached_response, estimate_complexity
from providers import call_llm
from template import DASHBOARD_HTML

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Router", version="1.0")

# ==================== SCHEMAS ====================

class ProviderCreate(BaseModel):
    name: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model_name: str
    tier: str

class ProductKeyCreate(BaseModel):
    name: str = "Company Product"
    company_name: str = ""

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# ==================== DASHBOARD ====================

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML

# ==================== ADMIN APIs ====================

@app.post("/admin/providers")
def add_provider(data: ProviderCreate, db: Session = Depends(get_db)):
    if data.tier not in ["cheap", "medium", "expensive"]:
        raise HTTPException(400, "tier must be cheap / medium / expensive")

    provider = Provider(
        name=data.name,
        api_key=data.api_key,
        base_url=data.base_url,
        model_name=data.model_name,
        tier=data.tier
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"message": "Provider added successfully", "id": provider.id}

@app.get("/admin/providers")
def list_providers(db: Session = Depends(get_db)):
    return db.query(Provider).filter(Provider.is_active == True).all()

@app.post("/admin/product-key")
def create_product_key(data: ProductKeyCreate, db: Session = Depends(get_db)):
    key = ProductKey.generate_key()
    product = ProductKey(
        key=key,
        name=data.name,
        company_name=data.company_name,
        is_active=True          # हमेशा ऑन रहेगी
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {
        "message": "Product Key generated successfully (Permanent)",
        "product_key": product.key,
        "name": product.name
    }

@app.get("/admin/product-keys")
def list_product_keys(db: Session = Depends(get_db)):
    return db.query(ProductKey).filter(ProductKey.is_active == True).all()

@app.delete("/admin/product-key/{key}")
def delete_product_key(key: str, db: Session = Depends(get_db)):
    product = db.query(ProductKey).filter(ProductKey.key == key).first()
    if not product:
        raise HTTPException(404, "Product Key not found")
    product.is_active = False
    db.commit()
    return {"message": "Product Key deactivated"}

# ==================== MAIN CHAT API ====================

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Product Key. Use: Bearer pk_xxxxx")

    product_key = authorization.replace("Bearer ", "").strip()

    product = db.query(ProductKey).filter(
        ProductKey.key == product_key,
        ProductKey.is_active == True
    ).first()

    if not product:
        raise HTTPException(401, "Invalid or deactivated Product Key")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    last_user_message = messages[-1]["content"] if messages else ""

    # 1. Cache check (Hello, Hi आदि)
    cached = get_cached_response(last_user_message)
    if cached:
        return {
            "id": "cached",
            "object": "chat.completion",
            "model": "cache",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": cached},
                "finish_reason": "stop"
            }],
            "routed_to": "cache (zero cost)"
        }

    # 2. Complexity
    tier = estimate_complexity(messages)

    # 3. उस tier का provider
    provider = db.query(Provider).filter(
        Provider.tier == tier,
        Provider.is_active == True
    ).first()

    if not provider:
        provider = db.query(Provider).filter(Provider.is_active == True).first()
        if not provider:
            raise HTTPException(500, "No providers configured")

    # 4. Call real model
    try:
        reply = await call_llm(provider, messages)
    except Exception as e:
        raise HTTPException(500, f"Model error: {str(e)}")

    return {
        "id": "router-response",
        "object": "chat.completion",
        "model": provider.model_name,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply},
            "finish_reason": "stop"
        }],
        "routed_to": f"{provider.tier.upper()} → {provider.name} ({provider.model_name})"
    }