import os
import uuid
import httpx
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# 1. Database Setup
DATABASE_URL = "sqlite:///./router.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    api_key = Column(String)
    base_url = Column(String)
    model_name = Column(String)

class ProductKey(Base):
    __tablename__ = "product_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    company_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    low_provider_id = Column(Integer, ForeignKey("providers.id"))
    medium_provider_id = Column(Integer, ForeignKey("providers.id"))
    hard_provider_id = Column(Integer, ForeignKey("providers.id"))

Base.metadata.create_all(bind=engine)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. FastAPI Setup
app = FastAPI(title="AI Router Console")

# Import HTML Template
from template import DASHBOARD_HTML

# Pydantic Schemas
class ProviderCreate(BaseModel):
    name: str
    api_key: str
    base_url: str
    model_name: str

class ProductKeyCreate(BaseModel):
    company_name: str
    low_provider_id: int
    medium_provider_id: int
    hard_provider_id: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "auto"
    messages: List[ChatMessage]

# 3. Web UI Route
@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return DASHBOARD_HTML

# 4. API Provider Routes
@app.post("/admin/providers/verify-and-add")
async def verify_and_add_provider(data: ProviderCreate, db: Session = Depends(get_db)):
    # Test API Key with a small payload
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {data.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": data.model_name,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5
            }
            url = f"{data.base_url.rstrip('/')}/chat/completions"
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
            if response.status_code != 200:
                return {"valid": False, "error": response.text}
    except Exception as e:
        return {"valid": False, "error": str(e)}

    # Save to DB if valid
    new_provider = Provider(**data.dict())
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return {"valid": True, "provider_id": new_provider.id}

@app.get("/admin/providers")
def get_providers(db: Session = Depends(get_db)):
    return db.query(Provider).all()

@app.post("/admin/product-key")
def create_product_key(data: ProductKeyCreate, db: Session = Depends(get_db)):
    gen_key = f"sk-prod-{uuid.uuid4().hex[:16]}"
    new_key = ProductKey(
        key=gen_key,
        company_name=data.company_name,
        low_provider_id=data.low_provider_id,
        medium_provider_id=data.medium_provider_id,
        hard_provider_id=data.hard_provider_id
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return {"product_key": gen_key, "company_name": data.company_name}

# 5. Strict Multi-Tenant History Routes
@app.get("/admin/history/{company_name}")
def get_isolated_history(company_name: str, db: Session = Depends(get_db)):
    history = db.query(ProductKey).filter(
        ProductKey.company_name == company_name,
        ProductKey.is_active == True
    ).all()
    
    return {
        "company": company_name,
        "history": [
            {
                "id": k.id,
                "key": k.key,
                "company_name": k.company_name,
                "is_active": k.is_active
            } for k in history
        ]
    }

@app.delete("/admin/history/delete/{key_id}")
def delete_isolated_key(key_id: int, db: Session = Depends(get_db)):
    key_obj = db.query(ProductKey).filter(ProductKey.id == key_id).first()
    if not key_obj:
        raise HTTPException(status_code=404, detail="Key not found")
        
    db.delete(key_obj)
    db.commit()
    return {"status": "success", "message": "Key permanently deleted"}

# 6. Core Router Dynamic Route
@app.post("/v1/chat/completions")
async def router_chat(
    request: ChatCompletionRequest,
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or Invalid API Key")
    
    prod_key_str = authorization.replace("Bearer ", "").strip()
    prod_key = db.query(ProductKey).filter(ProductKey.key == prod_key_str, ProductKey.is_active == True).first()
    
    if not prod_key:
        raise HTTPException(status_code=401, detail="Unauthorized Production Key")

    # Count prompt word length
    total_words = sum(len(msg.content.split()) for msg in request.messages)

    # Smart Routing Engine Logic
    if total_words < 50:
        selected_provider_id = prod_key.low_provider_id
    elif total_words < 150:
        selected_provider_id = prod_key.medium_provider_id
    else:
        selected_provider_id = prod_key.hard_provider_id

    provider = db.query(Provider).filter(Provider.id == selected_provider_id).first()
    if not provider:
        raise HTTPException(status_code=500, detail="Mapped Provider not found")

    # Proxy call to selected Provider
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": provider.model_name,
            "messages": [msg.dict() for msg in request.messages]
        }
        url = f"{provider.base_url.rstrip('/')}/chat/completions"
        
        try:
            res = await client.post(url, headers=headers, json=payload, timeout=60.0)
            return res.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Provider call failed: {str(e)}")
    
