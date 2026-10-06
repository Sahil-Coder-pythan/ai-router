from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets

from database import engine, get_db, Base
from models import Provider, ProductKey
from router_logic import estimate_response_complexity
from providers import call_llm, verify_provider_credentials
from template import DASHBOARD_HTML

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Powerful AI Router", version="3.2")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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


def get_client_id(x_client_id: Optional[str] = Header(None, alias="X-Client-Id")) -> str:
    """Silent per-browser identity. No login needed."""
    if x_client_id and len(x_client_id.strip()) >= 8:
        return x_client_id.strip()
    # fallback - should rarely happen if frontend works
    return "anonymous"


@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML


@app.post("/admin/providers/verify-and-add")
async def verify_and_add_provider(
    data: ProviderVerifyRequest,
    client_id: str = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    is_valid = await verify_provider_credentials(data.api_key, data.base_url, data.model_name)
    if not is_valid:
        return {"valid": False, "message": "Credentials check failed"}
    provider = Provider(
        client_id=client_id,
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
def list_providers(client_id: str = Depends(get_client_id), db: Session = Depends(get_db)):
    return db.query(Provider).filter(
        Provider.client_id == client_id,
        Provider.is_active == True
    ).all()


@app.delete("/admin/providers/{provider_id}")
def delete_provider(
    provider_id: int,
    client_id: str = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(
        Provider.id == provider_id,
        Provider.client_id == client_id
    ).first()
    if not provider:
        raise HTTPException(404, "Not found")
    provider.is_active = False
    db.commit()
    return {"success": True}


@app.get("/admin/product-keys")
def list_product_keys(client_id: str = Depends(get_client_id), db: Session = Depends(get_db)):
    keys = db.query(ProductKey).filter(
        ProductKey.client_id == client_id,
        ProductKey.is_active == True
    ).order_by(ProductKey.created_at.desc()).all()
    return [
        {"id": k.id, "key": k.key, "company_name": k.company_name, "name": k.name, "created_at": str(k.created_at)}
        for k in keys
    ]


@app.delete("/admin/product-keys/{key_id}")
def delete_product_key(
    key_id: int,
    client_id: str = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    product = db.query(ProductKey).filter(
        ProductKey.id == key_id,
        ProductKey.client_id == client_id
    ).first()
    if not product:
        raise HTTPException(404, "Not found")
    product.is_active = False
    db.commit()
    return {"success": True}


@app.post("/admin/product-key")
def create_product_key(
    data: ProductKeyCreateRequest,
    client_id: str = Depends(get_client_id),
    db: Session = Depends(get_db)
):
    for pid in [data.low_provider_id, data.medium_provider_id, data.hard_provider_id]:
        p = db.query(Provider).filter(
            Provider.id == pid, Provider.client_id == client_id, Provider.is_active == True
        ).first()
        if not p:
            raise HTTPException(400, f"Provider {pid} not found")
    key = ProductKey.generate_key()
    product = ProductKey(
        client_id=client_id,
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
@limiter.limit("120/minute")
async def chat_completions(
    request: Request,
    data: ChatRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Production Key")
    product_key_str = authorization.replace("Bearer ", "").strip()
    product = db.query(ProductKey).filter(
        ProductKey.key == product_key_str, ProductKey.is_active == True
    ).first()
    if not product:
        raise HTTPException(401, "Invalid Production Key")
    messages = [{"role": m.role, "content": m.content} for m in data.messages]
    complexity = estimate_response_complexity(messages)
    if complexity == "hard":
        provider = product.hard_provider
    elif complexity == "medium":
        provider = product.medium_provider
    else:
        provider = product.low_provider
    if not provider or not provider.is_active:
        raise HTTPException(500, "Mapped API key not found or deleted")
    try:
        reply = await call_llm(provider, messages)
    except Exception as e:
        raise HTTPException(500, f"Model Error: {str(e)}")
    return {
        "id": "router-response",
        "object": "chat.completion",
        "model": provider.model_name,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
        "routed_to": f"{complexity.upper()} -> {provider.name} ({provider.model_name})"
    }
