import hashlib
import hmac
import os
import re
import secrets

import bcrypt
import httpx
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text, Column, Integer, Boolean
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
from models import Provider, ProductKey, UsageLog, User, EmailCode
from router_logic import estimate_response_complexity
from providers import call_llm, verify_provider_credentials
from template import DASHBOARD_HTML, LOGIN_HTML

# ==============================================================================
# OWNER OFF/ON SWITCH (Render > Environment: ADMIN_SECRET, optional PAYMENT_URL)
# ==============================================================================
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "").strip()
PAYMENT_URL = os.getenv("PAYMENT_URL", "").strip()
PLAN_PRICE = os.getenv("PLAN_PRICE", "$300").strip()
CONTACT_PHONE = os.getenv("CONTACT_PHONE", "").strip()


class ServiceSwitch(Base):
    __tablename__ = "service_switch"
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)


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
# OWNER OFF/ON SWITCH - guard + endpoints
# ==============================================================================
PAY_MSG = "Payment Required - कृपया पेमेंट करें - Please complete payment - Upgrade Now"

from html import escape as _html_escape

# PLAN_PRICE me sirf amount likho (jaise 500). "$" aur "/ month" code khud lagata hai.
_amount = "".join(ch for ch in PLAN_PRICE if ch in "0123456789.,") or "300"
_PRICE_TEXT = "$" + _amount

_PHONE_CLEAN = "".join(ch for ch in CONTACT_PHONE if ch in "+0123456789 -()")
_CONTACT = ""
if _PHONE_CLEAN:
    _tel = "".join(ch for ch in _PHONE_CLEAN if ch in "+0123456789")
    _CONTACT += (
        '<p class="lbl">Call us to complete your payment</p>'
        '<a class="call" href="tel:' + _tel + '">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 '
        '19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 '
        '9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'
        '<span>' + _PHONE_CLEAN + '</span></a>'
    )
if PAYMENT_URL:
    _CONTACT += '<a class="alt" href="' + PAYMENT_URL + '">Or pay online</a>'
if not _CONTACT:
    _CONTACT = '<p class="lbl">Please contact the owner to complete your payment.</p>'

PAY_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#070b17">
<title>Payment Required</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;min-height:100%}
body{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:28px 20px;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans Devanagari",Arial,sans-serif;
color:#e5e9f5;text-align:center;background:#070b17;position:relative;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
background:radial-gradient(700px 420px at 12% -8%,rgba(99,102,241,.38),transparent 62%),
radial-gradient(640px 420px at 105% 105%,rgba(16,185,129,.22),transparent 60%),
radial-gradient(500px 300px at 50% 50%,rgba(139,92,246,.10),transparent 70%)}
body:after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.5;
background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:44px 44px;
-webkit-mask-image:radial-gradient(ellipse at center,#000 30%,transparent 75%);
mask-image:radial-gradient(ellipse at center,#000 30%,transparent 75%)}
.wrap{position:relative;z-index:1;width:100%;max-width:430px;animation:rise .7s cubic-bezier(.2,.8,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(251,191,36,.6)}70%{box-shadow:0 0 0 9px rgba(251,191,36,0)}100%{box-shadow:0 0 0 0 rgba(251,191,36,0)}}
.pill{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:999px;font-size:12.5px;
font-weight:600;letter-spacing:.3px;color:#fde68a;background:rgba(251,191,36,.10);border:1px solid rgba(251,191,36,.28)}
.pill i{width:8px;height:8px;border-radius:50%;background:#fbbf24;animation:pulse 1.8s infinite}
.lock{width:84px;height:84px;margin:26px auto 24px;border-radius:26px;display:flex;align-items:center;
justify-content:center;color:#fff;position:relative;background:linear-gradient(145deg,#6366f1,#8b5cf6 60%,#a855f7);
box-shadow:0 18px 50px rgba(99,102,241,.5),inset 0 1px 0 rgba(255,255,255,.35)}
.lock:after{content:"";position:absolute;inset:-9px;border-radius:32px;border:1px solid rgba(139,92,246,.35)}
h1{margin:0;font-size:32px;font-weight:800;letter-spacing:-.8px;color:#fff;line-height:1.15}
.hi{margin:10px 0 0;font-size:21px;font-weight:700;color:#c4b5fd}
.sub{margin:16px auto 0;max-width:350px;font-size:15px;line-height:1.65;color:#8b97b3}
.mini{margin-top:26px;font-size:15px;color:#8b97b3}
.mini b{color:#fff;font-size:22px;font-weight:800;letter-spacing:-.5px}
.cta{margin-top:12px;width:100%;display:flex;align-items:center;justify-content:center;gap:10px;
padding:17px 24px;border:0;border-radius:16px;cursor:pointer;font-size:17px;font-weight:700;color:#fff;
background:linear-gradient(135deg,#22c55e,#059669);box-shadow:0 14px 34px rgba(16,185,129,.38),inset 0 1px 0 rgba(255,255,255,.3);
transition:transform .15s,box-shadow .2s}
.cta:hover{box-shadow:0 18px 40px rgba(16,185,129,.5),inset 0 1px 0 rgba(255,255,255,.3)}
.cta:active{transform:scale(.98)}
.cta svg{transition:transform .25s}
.cta.open svg{transform:rotate(180deg)}
.panel{display:none;margin-top:22px;text-align:left;padding:28px 26px;border-radius:24px;
background:linear-gradient(#0e1528,#0e1528) padding-box,linear-gradient(135deg,rgba(99,102,241,.9),rgba(16,185,129,.7)) border-box;
border:1px solid transparent;box-shadow:0 30px 70px rgba(0,0,0,.5);animation:rise .45s cubic-bezier(.2,.8,.2,1) both}
.panel.show{display:block}
.top{display:flex;align-items:center;justify-content:space-between}
.badge{padding:6px 13px;border-radius:999px;font-size:11.5px;font-weight:800;letter-spacing:1px;
text-transform:uppercase;color:#c7d2fe;background:rgba(99,102,241,.2);border:1px solid rgba(99,102,241,.4)}
.sec{font-size:12.5px;color:#7a86a3;display:flex;align-items:center;gap:6px}
.price{margin:20px 0 4px;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
.price strong{font-size:58px;font-weight:800;letter-spacing:-2.5px;color:#fff;line-height:1}
.price small{font-size:17px;font-weight:600;color:#8b97b3}
.desc{margin:6px 0 0;font-size:14px;color:#7a86a3}
hr{border:0;height:1px;background:rgba(255,255,255,.09);margin:22px 0}
ul{list-style:none;margin:0 0 24px;padding:0}
li{display:flex;align-items:center;gap:12px;margin:14px 0;font-size:15px;color:#d5dbee}
li span{flex:none;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;
background:rgba(16,185,129,.16);color:#34d399}
.pay{width:100%;padding:16px 24px;border:0;border-radius:16px;cursor:pointer;font-size:17px;font-weight:700;color:#fff;
background:linear-gradient(135deg,#6366f1,#8b5cf6);box-shadow:0 14px 34px rgba(99,102,241,.42),inset 0 1px 0 rgba(255,255,255,.3);
transition:transform .15s}
.pay:active{transform:scale(.98)}
.contact{display:none;text-align:center;animation:rise .4s cubic-bezier(.2,.8,.2,1) both}
.contact.show{display:block}
.lbl{margin:0 0 14px;font-size:14px;color:#8b97b3}
.call{display:flex;align-items:center;justify-content:center;gap:12px;padding:17px 20px;border-radius:16px;
font-size:24px;font-weight:800;letter-spacing:.8px;color:#fff;text-decoration:none;
background:linear-gradient(135deg,rgba(16,185,129,.22),rgba(16,185,129,.1));border:1px solid rgba(52,211,153,.5)}
.alt{display:block;margin-top:16px;font-size:14px;color:#a5b4fc;text-decoration:underline}
.foot{margin-top:26px;font-size:12.5px;color:#5d6985;line-height:1.6}
</style></head>
<body>
<div class="wrap">
<div class="pill"><i></i>Service paused</div>
<div class="lock"><svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor"
stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2.5"/>
<path d="M8 11V7a4 4 0 0 1 8 0v4"/><circle cx="12" cy="16" r="1.2" fill="currentColor"/></svg></div>
<h1>Payment Required</h1>
<div class="hi">कृपया पेमेंट करें</div>
<p class="sub">Your access is currently paused. Please complete your payment to continue using this service.</p>
<div class="mini"><b>__PRICE__</b> / month</div>
<button class="cta" id="up" onclick="var p=document.getElementById('plan');p.classList.toggle('show');this.classList.toggle('open')">
<span>Upgrade Now</span>
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
</button>
<div class="panel" id="plan">
<div class="top"><span class="badge">Pro Plan</span>
<span class="sec"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 4 5v6c0 5 3.4 9.3 8 11 4.6-1.7 8-6 8-11V5z"/></svg>Secure</span></div>
<div class="price"><strong>__PRICE__</strong><small>/ month</small></div>
<p class="desc">Everything you need, billed monthly.</p>
<hr>
<ul>
<li><span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></span>Full AI Router access</li>
<li><span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></span>Dashboard and usage stats</li>
<li><span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></span>Production keys for your team</li>
</ul>
<button class="pay" onclick="document.getElementById('ct').classList.add('show');this.style.display='none'">Pay Now</button>
<div class="contact" id="ct">__CONTACT__</div>
</div>
<div class="foot">Service resumes right after your payment is confirmed.</div>
</div>
</body></html>""".replace("__PRICE__", _PRICE_TEXT).replace("__CONTACT__", _CONTACT)


def _is_on() -> bool:
    db = None
    try:
        db = next(get_db())
        sw = db.query(ServiceSwitch).first()
        return True if sw is None else bool(sw.enabled)
    except Exception:
        return True
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass


@app.middleware("http")
async def service_guard(request: Request, call_next):
    if request.url.path.startswith("/owner/"):
        return await call_next(request)
    if not _is_on():
        if request.url.path == "/":
            return HTMLResponse(PAY_HTML, status_code=402, headers={"Cache-Control": "no-store"})
        return JSONResponse({"error": PAY_MSG}, status_code=402)
    return await call_next(request)


def require_owner(x_owner_secret: Optional[str] = Header(None, alias="X-Owner-Secret")):
    if not ADMIN_SECRET or not hmac.compare_digest(x_owner_secret or "", ADMIN_SECRET):
        raise HTTPException(403, "Forbidden")


@app.post("/owner/switch/{state}")
def owner_switch(state: str, _=Depends(require_owner), db: Session = Depends(get_db)):
    if state not in ("on", "off"):
        raise HTTPException(400, "use on or off")
    sw = db.query(ServiceSwitch).first()
    if not sw:
        sw = ServiceSwitch(id=1)
        db.add(sw)
    sw.enabled = (state == "on")
    db.commit()
    return {"enabled": sw.enabled}


@app.get("/owner/status")
def owner_status(_=Depends(require_owner), db: Session = Depends(get_db)):
    sw = db.query(ServiceSwitch).first()
    return {"enabled": True if sw is None else bool(sw.enabled)}

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

# ==============================================================================
# EMAIL SETTINGS (verification code bhejne ke liye)
# Render free plan SMTP band rakhta hai, isliye Brevo ka HTTPS API use hota hai.
# Render > Environment me ye do daalne hain:
#   BREVO_API_KEY  = Brevo ki API key
#   MAIL_FROM      = Brevo me verify ki hui bhejne wali email
# Ye set nahi hain to: signup bina code ke chalega, aur forgot password band rahega.
# ==============================================================================
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "").strip()
MAIL_FROM = os.getenv("MAIL_FROM", "").strip()
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Stratic Soft").strip()
MAIL_ENABLED = bool(BREVO_API_KEY and MAIL_FROM)

CODE_TTL_MINUTES = 10
RESET_TOKEN_TTL_MINUTES = 15
MAX_CODE_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def _now():
    return datetime.now(timezone.utc)


def _make_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def _hash_code(email: str, purpose: str, code: str) -> str:
    message = f"{email}|{purpose}|{code}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()


async def send_email(to_email: str, subject: str, text_body: str, html_body: str) -> bool:
    if not MAIL_ENABLED:
        return False

    payload = {
        "sender": {"name": MAIL_FROM_NAME, "email": MAIL_FROM},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_body,
        "htmlContent": html_body,
    }
    headers = {
        "api-key": BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post("https://api.brevo.com/v3/smtp/email", headers=headers, json=payload)
        if res.status_code >= 300:
            print("Email send failed:", res.status_code, res.text[:200])
            return False
        return True
    except Exception as e:
        print("Email send error:", str(e))
        return False


def _code_email(code: str, purpose: str):
    if purpose == "signup":
        subject = "Verify your email - Stratic Soft"
        intro = "Use this code to verify your email and finish creating your account."
    else:
        subject = "Reset your password - Stratic Soft"
        intro = "Use this code to reset your password."

    text_body = (
        f"{intro}\n\nYour verification code: {code}\n\n"
        f"This code expires in {CODE_TTL_MINUTES} minutes. "
        "If you did not request it, you can safely ignore this email."
    )
    html_body = (
        '<div style="font-family:Arial,sans-serif;max-width:420px;margin:0 auto;padding:24px;">'
        '<div style="font-size:20px;font-weight:800;color:#172033;">Stratic Soft</div>'
        f'<p style="color:#475569;font-size:15px;">{intro}</p>'
        '<div style="font-size:34px;font-weight:800;letter-spacing:8px;color:#4f46e5;'
        f'background:#f1f5f9;border-radius:14px;padding:16px;text-align:center;">{code}</div>'
        f'<p style="color:#64748b;font-size:13px;">This code expires in {CODE_TTL_MINUTES} minutes. '
        'If you did not request it, you can safely ignore this email.</p>'
        '</div>'
    )
    return subject, text_body, html_body


def _save_code(db, email: str, purpose: str, name=None, password_hash=None) -> str:
    """Purane code hata kar naya code banata hai. Code wapas deta hai (DB me sirf hash jaata hai)."""
    db.query(EmailCode).filter(EmailCode.email == email, EmailCode.purpose == purpose).delete()
    db.query(EmailCode).filter(EmailCode.expires_at < _now()).delete()

    code = _make_code()
    row = EmailCode(
        email=email,
        purpose=purpose,
        code_hash=_hash_code(email, purpose, code),
        name=name,
        password_hash=password_hash,
        verified=False,
        attempts=0,
        last_sent_at=_now(),
        expires_at=_now() + timedelta(minutes=CODE_TTL_MINUTES),
    )
    db.add(row)
    db.commit()
    return code


def _check_code(db, email: str, purpose: str, code: str):
    """Code sahi hai ya nahi dekhta hai. Galat ho to error, 5 galat ke baad code band."""
    row = db.query(EmailCode).filter(
        EmailCode.email == email,
        EmailCode.purpose == purpose
    ).first()

    if row is None or row.verified or _aware(row.expires_at) < _now():
        raise HTTPException(400, "This code is invalid or has expired. Please request a new one.")

    if row.attempts >= MAX_CODE_ATTEMPTS:
        db.delete(row)
        db.commit()
        raise HTTPException(400, "Too many wrong attempts. Please request a new code.")

    entered = re.sub(r"[^0-9]", "", code or "")
    if not hmac.compare_digest(row.code_hash, _hash_code(email, purpose, entered)):
        row.attempts = (row.attempts or 0) + 1
        left = MAX_CODE_ATTEMPTS - row.attempts
        if left <= 0:
            db.delete(row)
            db.commit()
            raise HTTPException(400, "Too many wrong attempts. Please request a new code.")
        db.commit()
        raise HTTPException(400, f"Incorrect code. {left} attempt(s) left.")

    return row


def _clean_email(raw: str) -> str:
    email = (raw or "").strip().lower()
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise HTTPException(400, "Please enter a valid email address")
    return email


def _check_new_password(password: str):
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(400, "Password must be 72 characters or less")


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


class EmailOnlyRequest(BaseModel):
    email: str


class CodeRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    reset_token: str
    new_password: str


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
async def auth_signup(request: Request, data: SignupRequest, db: Session = Depends(get_db)):
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

    password_hash = hash_password(password)

    # Email service set nahi hai to seedha account ban jayega (pehle jaisa)
    if not MAIL_ENABLED:
        user = User(name=name, email=email, password_hash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)

        request.session.clear()
        request.session["user_id"] = user.id
        return {"ok": True}

    # Email service set hai: pehle verification code bhejo, account code sahi hone par banega
    code = _save_code(db, email, "signup", name=name, password_hash=password_hash)
    subject, text_body, html_body = _code_email(code, "signup")
    sent = await send_email(email, subject, text_body, html_body)
    if not sent:
        db.query(EmailCode).filter(EmailCode.email == email, EmailCode.purpose == "signup").delete()
        db.commit()
        raise HTTPException(502, "We could not send the verification email. Please try again in a moment.")

    return {"verify": True, "email": email}


@app.post("/auth/signup/verify")
@limiter.limit("15/minute", key_func=_client_ip)
def auth_signup_verify(request: Request, data: CodeRequest, db: Session = Depends(get_db)):
    email = _clean_email(data.email)
    row = _check_code(db, email, "signup", data.code)

    if db.query(User).filter(User.email == email).first():
        db.delete(row)
        db.commit()
        raise HTTPException(400, "An account with this email already exists. Please log in.")

    user = User(
        name=(row.name or email.split("@")[0])[:40],
        email=email,
        password_hash=row.password_hash,
    )
    db.add(user)
    db.delete(row)
    db.commit()
    db.refresh(user)

    request.session.clear()
    request.session["user_id"] = user.id
    return {"ok": True}


@app.post("/auth/signup/resend")
@limiter.limit("5/minute", key_func=_client_ip)
async def auth_signup_resend(request: Request, data: EmailOnlyRequest, db: Session = Depends(get_db)):
    if not MAIL_ENABLED:
        raise HTTPException(503, "Email service is not set up yet.")

    email = _clean_email(data.email)
    row = db.query(EmailCode).filter(
        EmailCode.email == email,
        EmailCode.purpose == "signup"
    ).first()

    if row is None:
        raise HTTPException(400, "Please start sign up again.")

    waited = (_now() - _aware(row.last_sent_at)).total_seconds()
    if waited < RESEND_COOLDOWN_SECONDS:
        raise HTTPException(429, f"Please wait {int(RESEND_COOLDOWN_SECONDS - waited) + 1} seconds before requesting a new code.")

    code = _save_code(db, email, "signup", name=row.name, password_hash=row.password_hash)
    subject, text_body, html_body = _code_email(code, "signup")
    sent = await send_email(email, subject, text_body, html_body)
    if not sent:
        raise HTTPException(502, "We could not send the email. Please try again in a moment.")

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


@app.post("/auth/forgot")
@limiter.limit("5/minute", key_func=_client_ip)
async def auth_forgot(request: Request, data: EmailOnlyRequest, db: Session = Depends(get_db)):
    if not MAIL_ENABLED:
        raise HTTPException(503, "Password reset by email is not set up yet.")

    email = _clean_email(data.email)
    user = db.query(User).filter(User.email == email).first()

    # Account hai ya nahi, bahar se pata nahi chalna chahiye - jawab hamesha same
    if user is not None:
        existing = db.query(EmailCode).filter(
            EmailCode.email == email,
            EmailCode.purpose == "reset"
        ).first()

        recently_sent = (
            existing is not None
            and (_now() - _aware(existing.last_sent_at)).total_seconds() < RESEND_COOLDOWN_SECONDS
        )

        if not recently_sent:
            code = _save_code(db, email, "reset")
            subject, text_body, html_body = _code_email(code, "reset")
            sent = await send_email(email, subject, text_body, html_body)
            if not sent:
                print("Forgot-password email could not be sent")

    return {"ok": True}


@app.post("/auth/forgot/verify")
@limiter.limit("15/minute", key_func=_client_ip)
def auth_forgot_verify(request: Request, data: CodeRequest, db: Session = Depends(get_db)):
    email = _clean_email(data.email)
    row = _check_code(db, email, "reset", data.code)

    token = secrets.token_urlsafe(32)
    row.reset_token_hash = _hash_code(email, "token", token)
    row.verified = True
    row.attempts = 0
    row.expires_at = _now() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
    db.commit()

    return {"reset_token": token}


@app.post("/auth/forgot/reset")
@limiter.limit("10/minute", key_func=_client_ip)
def auth_forgot_reset(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = _clean_email(data.email)
    _check_new_password(data.new_password)

    row = db.query(EmailCode).filter(
        EmailCode.email == email,
        EmailCode.purpose == "reset"
    ).first()

    expired_msg = "Your reset session has expired. Please start again."

    if (
        row is None
        or not row.verified
        or not row.reset_token_hash
        or _aware(row.expires_at) < _now()
        or not hmac.compare_digest(row.reset_token_hash, _hash_code(email, "token", data.reset_token or ""))
    ):
        raise HTTPException(400, expired_msg)

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(400, expired_msg)

    # Sirf password badalta hai - account, API keys, history sab wahi rehte hain
    user.password_hash = hash_password(data.new_password)
    db.delete(row)
    db.commit()

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

    if request.query_params.get("error"):
        # User ne Google screen par Cancel / Deny dabaya
        return RedirectResponse("/?error=google_cancelled")

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
            if not MAIL_ENABLED:
                # Email verification band hai to pehle se bana password hata dete hain,
                # taaki kisi ne dusre ki email se account bana rakha ho to wo andar na aa sake.
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
    """All-time real request counts per API key.
    - Requests belonging to deleted Production Keys are excluded from totals.
    - Soft-deleted API Keys still appear (with is_active=False) so the UI can show a badge.
    """
    all_providers = db.query(Provider).filter(
        Provider.client_id == client_id
    ).all()

    active_pk_ids = {
        pk.id for pk in db.query(ProductKey).filter(
            ProductKey.client_id == client_id,
            ProductKey.is_active == True
        ).all()
    }

    logs = db.query(UsageLog).filter(
        UsageLog.client_id == client_id
    ).all()

    stats = {}
    for p in all_providers:
        stats[p.id] = {
            "provider_id": p.id,
            "name": p.name,
            "model_name": p.model_name,
            "is_active": bool(p.is_active),
            "requests": 0,
            "success": 0,
            "failed": 0,
        }

    for log in logs:
        # Skip logs that belong to a deleted Production Key
        if log.product_key_id is not None and log.product_key_id not in active_pk_ids:
            continue

        pid = log.provider_id
        if pid is None:
            continue
        if pid not in stats:
            stats[pid] = {
                "provider_id": pid,
                "name": log.provider_name or "Unknown",
                "model_name": log.model_name or "",
                "is_active": False,
                "requests": 0,
                "success": 0,
                "failed": 0,
            }
        stats[pid]["requests"] += 1
        if log.success:
            stats[pid]["success"] += 1
        else:
            stats[pid]["failed"] += 1

    # Keep active providers + any deleted ones that still have remaining requests
    rows = [r for r in stats.values() if r["is_active"] or r["requests"] > 0]
    rows.sort(key=lambda x: (not x["is_active"], -x["requests"]))

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

    def _log_usage(success: bool, prov=None):
        """Jawab mila to success=True, nahi mila / error to success=False."""
        try:
            p = prov if prov is not None else provider
            log = UsageLog(
                client_id=product.client_id or "",
                provider_id=p.id if p else None,
                product_key_id=product.id,
                provider_name=(p.name if p else "") or "",
                model_name=(p.model_name if p else "") or "",
                complexity=complexity,
                success=success
            )
            db.add(log)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

    if not provider or not provider.is_active:
        _log_usage(False, provider)
        raise HTTPException(500, "Mapped API key not found or deleted")

    try:
        reply = await call_llm(provider, messages)
        _log_usage(True, provider)
    except Exception as e:
        _log_usage(False, provider)
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