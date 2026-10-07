from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import engine, get_db, Base
from models import Provider, ProductKey, UsageLog
from router_logic import estimate_response_complexity
from providers import call_llm, verify_provider_credentials
from template import DASHBOARD_HTML

Base.metadata.create_all(bind=engine)


def _migrate_client_id():
    with engine.connect() as conn:
        try:
            if "sqlite" in str(engine.url):
                cols_p = [r[1] for r in conn.execute(sql_text("PRAGMA table_info(providers)")).fetchall()]
                cols_k = [r[1] for r in conn.execute(sql_text("PRAGMA table_info(product_keys)")).fetchall()]
                if "client_id" not in cols_p:
                    conn.execute(sql_text("ALTER TABLE providers ADD COLUMN client_id VARCHAR DEFAULT ''"))
                    conn.commit()
                if "client_id" not in cols_k:
                    conn.execute(sql_text("ALTER TABLE product_keys ADD COLUMN client_id VARCHAR DEFAULT ''"))
                    conn.commit()
            else:
                conn.execute(sql_text("ALTER TABLE providers ADD COLUMN IF NOT EXISTS client_id VARCHAR DEFAULT ''"))
                conn.execute(sql_text("ALTER TABLE product_keys ADD COLUMN IF NOT EXISTS client_id VARCHAR DEFAULT ''"))
                conn.commit()
        except Exception as e:
            print("Migration note:", e)


_migrate_client_id()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Powerful AI Router", version="3.5")
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
    if x_client_id and len(x_client_id.strip()) >= 8:
        return x_client_id.strip()
    return "anonymous"


def _aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def dashboard_page():
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
        {
            "id": k.id,
            "key": k.key,
            "company_name": k.company_name,
            "name": k.name,
            "created_at": str(k.created_at)
        }
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
            Provider.id == pid,
            Provider.client_id == client_id,
            Provider.is_active == True
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


@app.get("/admin/usage-stats")
def usage_stats(client_id: str = Depends(get_client_id), db: Session = Depends(get_db)):
    """All-time real request counts per API key: total / success / failed."""
    providers = db.query(Provider).filter(
        Provider.client_id == client_id,
        Provider.is_active == True
    ).all()

    logs = db.query(UsageLog).filter(
        UsageLog.client_id == client_id
    ).all()

    stats = {}
    for p in providers:
        stats[p.id] = {
            "provider_id": p.id,
            "name": p.name,
            "model_name": p.model_name,
            "requests": 0,
            "success": 0,
            "failed": 0,
        }

    for log in logs:
        pid = log.provider_id
        if pid is None:
            continue
        if pid not in stats:
            # provider may have been soft-deleted; still show if has logs
            stats[pid] = {
                "provider_id": pid,
                "name": log.provider_name or "Unknown",
                "model_name": log.model_name or "",
                "requests": 0,
                "success": 0,
                "failed": 0,
            }
        stats[pid]["requests"] += 1
        if log.success:
            stats[pid]["success"] += 1
        else:
            stats[pid]["failed"] += 1

    rows = list(stats.values())
    rows.sort(key=lambda x: x["requests"], reverse=True)

    total_requests = sum(r["requests"] for r in rows)
    total_success = sum(r["success"] for r in rows)
    total_failed = sum(r["failed"] for r in rows)

    return {
        "totals": {
            "requests": total_requests,
            "success": total_success,
            "failed": total_failed,
        },
        "providers": rows,
    }


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
        ProductKey.key == product_key_str,
        ProductKey.is_active == True
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
        log = UsageLog(
            client_id=product.client_id or "",
            provider_id=provider.id,
            product_key_id=product.id,
            provider_name=provider.name,
            model_name=provider.model_name,
            complexity=complexity,
            success=True
        )
        db.add(log)
        db.commit()
    except Exception as e:
        try:
            log = UsageLog(
                client_id=product.client_id or "",
                provider_id=provider.id if provider else None,
                product_key_id=product.id,
                provider_name=provider.name if provider else "",
                model_name=provider.model_name if provider else "",
                complexity=complexity,
                success=False
            )
            db.add(log)
            db.commit()
        except Exception:
            pass
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
