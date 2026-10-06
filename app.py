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
    """Real request counts per provider: last 60s, last hour, today."""
    now = datetime.now(timezone.utc)
    start_minute = now - timedelta(seconds=60)
    start_hour = now - timedelta(hours=1)
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Only this client's logs
    logs = db.query(UsageLog).filter(
        UsageLog.client_id == client_id,
        UsageLog.created_at >= start_day
    ).all()

    # Also load providers for names
    providers = db.query(Provider).filter(
        Provider.client_id == client_id,
        Provider.is_active == True
    ).all()
    provider_map = {p.id: p for p in providers}

    # Aggregate
    stats = {}  # provider_id -> {name, model, minute, hour, day}

    def ensure(pid, name="", model=""):
        if pid not in stats:
            stats[pid] = {
                "provider_id": pid,
                "name": name,
                "model_name": model,
                "minute": 0,
                "hour": 0,
                "day": 0
            }

    for p in providers:
        ensure(p.id, p.name, p.model_name)

    for log in logs:
        pid = log.provider_id or 0
        name = log.provider_name or (provider_map[pid].name if pid in provider_map else "Unknown")
        model = log.model_name or (provider_map[pid].model_name if pid in provider_map else "")
        ensure(pid, name, model)
        ts = _aware(log.created_at)
        if ts is None:
            continue
        stats[pid]["day"] += 1
        if ts >= start_hour:
            stats[pid]["hour"] += 1
        if ts >= start_minute:
            stats[pid]["minute"] += 1

    rows = list(stats.values())
    rows.sort(key=lambda x: x["day"], reverse=True)

    total_day = sum(r["day"] for r in rows)
    total_hour = sum(r["hour"] for r in rows)
    total_minute = sum(r["minute"] for r in rows)
    top = rows[0] if rows else None

    # Chart: last 24 hours hourly buckets per provider (for bar chart)
    hour_buckets = defaultdict(lambda: defaultdict(int))  # hour_label -> provider_name -> count
    for log in logs:
        ts = _aware(log.created_at)
        if ts is None:
            continue
        label = ts.strftime("%H:00")
        pname = log.provider_name or "Unknown"
        hour_buckets[label][pname] += 1

    # sorted hour labels for today
    labels = []
    for h in range(24):
        labels.append(f"{h:02d}:00")

    provider_names = sorted(set(r["name"] for r in rows if r["name"]))
    chart_series = []
    colors = ["#2563eb", "#7c3aed", "#06b6d4", "#f59e0b", "#ef4444", "#22c55e", "#ec4899"]
    for i, pname in enumerate(provider_names):
        data = [hour_buckets[lab].get(pname, 0) for lab in labels]
        chart_series.append({
            "name": pname,
            "data": data,
            "color": colors[i % len(colors)]
        })

    return {
        "now": now.isoformat(),
        "totals": {
            "minute": total_minute,
            "hour": total_hour,
            "day": total_day
        },
        "providers": rows,
        "top_provider": top,
        "chart": {
            "labels": labels,
            "series": chart_series
        }
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
