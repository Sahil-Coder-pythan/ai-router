import os
import re
import secrets

import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import engine, get_db, Base
from models import Provider, ProductKey, UsageLog, User
from router_logic import estimate_response_complexity
from providers import call_llm, verify_provider_credentials
from template import DASHBOARD_HTML, LOGIN_HTML

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

# ==============================================================================
# LOGIN SYSTEM SETTINGS (Render > Environment Variables se aate hain)
# ==============================================================================
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    # Set nahi hai to random key banegi (har restart par sab logout ho jayenge)
    SECRET_KEY = secrets.token_urlsafe(48)
    print("WARNING: SECRET_KEY set nahi hai. Render Environment me SECRET_KEY zaroor daalo.")

PUBLIC_URL = os.getenv("PUBLIC_URL", "https://ai-router-09d2.onrender.com").strip().rstrip("/")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="router_session",
    max_age=60 * 60 * 24 * 30,
    same_site="lax",
    https_only=bool(os.getenv("RENDER")),
)

oauth = OAuth()
if GOOGLE_ENABLED:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _client_ip(request: Request) -> str:
    # Render proxy ke peeche asli user ka IP X-Forwarded-For me aata hai
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


def hash_password(password: str) -> str:
    """Password kabhi seedha save nahi hota, sirf bcrypt hash save hota hai."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


_DUMMY_HASH = hash_password("dummy-password-for-timing")


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


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        request.session.clear()
    return user


def get_client_id(request: Request, db: Session = Depends(get_db)) -> str:
    """Ab client_id login hue user se aati hai (browser se nahi)."""
    user = _current_user(request, db)
    if user is None:
        raise HTTPException(401, "Login required")
    return f"user_{user.id}"


def _aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@app.get("/", response_class=HTMLResponse)
@app.head("/", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    headers = {"Cache-Control": "no-store"}
    if _current_user(request, db) is None:
        return HTMLResponse(LOGIN_HTML, headers=headers)
    return HTMLResponse(DASHBOARD_HTML, headers=headers)


# ==============================================================================
# AUTH ROUTES (Signup / Login / Google / Logout / Profile)
# ==============================================================================
@app.post("/auth/signup")
@limiter.limit("10/minute", key_func=_client_ip)
def auth_signup(request: Request, data: SignupRequest, db: Session = Depends(get_db)):
    name = data.name.strip()
    email = data.email.strip().lower()
    password = data.password

    if not name:
        raise HTTPException(400, "Please enter your name")
    if len(name) > 40:
        raise HTTPException(400, "Name must be 40 characters or less")
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise HTTPException(400, "Please enter a valid email address")
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(400, "Password must be 72 characters or less")

    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        if existing.google_id and not existing.password_hash:
            raise HTTPException(400, "This email is registered with Google. Please use Continue with Google.")
        raise HTTPException(400, "An account with this email already exists. Please log in.")

    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session.clear()
    request.session["user_id"] = user.id
    return {"ok": True}


@app.post("/auth/login")
@limiter.limit("10/minute", key_func=_client_ip)
def auth_login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        check_password(data.password, _DUMMY_HASH)  # timing barabar rakhne ke liye
        raise HTTPException(401, "Incorrect email or password")

    if not user.password_hash:
        raise HTTPException(401, "This account uses Google sign-in. Please use Continue with Google.")

    if not check_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")

    request.session.clear()
    request.session["user_id"] = user.id
    return {"ok": True}


@app.post("/auth/logout")
def auth_logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/auth/me")
def auth_me(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    if user is None:
        raise HTTPException(401, "Login required")
    return {"name": user.name or "", "email": user.email}


@app.get("/auth/google/login")
async def auth_google_login(request: Request):
    if not GOOGLE_ENABLED:
        return RedirectResponse("/?error=google_not_configured")
    redirect_uri = f"{PUBLIC_URL}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    if not GOOGLE_ENABLED:
        return RedirectResponse("/?error=google_not_configured")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print("Google login error:", str(e))
        return RedirectResponse("/?error=google_failed")

    info = token.get("userinfo") or {}
    email = (info.get("email") or "").strip().lower()
    google_sub = info.get("sub")

    if not email or not google_sub or not info.get("email_verified"):
        return RedirectResponse("/?error=google_failed")

    user = db.query(User).filter(User.google_id == google_sub).first()

    if user is None:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(
                email=email,
                name=(info.get("name") or email.split("@")[0])[:40],
                google_id=google_sub,
            )
            db.add(user)
        else:
            # Google ne prove kar diya ki email ka asli maalik yahi hai.
            # Kisi ne pehle se is email par password se account bana rakha ho to
            # woh password hata dete hain, taaki koi aur andar na aa sake.
            user.google_id = google_sub
            user.password_hash = None
        db.commit()
        db.refresh(user)

    request.session.clear()
    request.session["user_id"] = user.id
    return RedirectResponse("/")


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