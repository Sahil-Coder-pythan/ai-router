from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base
import secrets

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    base_url = Column(String, default="https://api.openai.com/v1")
    model_name = Column(String, nullable=False)
    tier = Column(String, nullable=False)          # cheap / medium / expensive
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProductKey(Base):
    __tablename__ = "product_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, default="Company Product")
    company_name = Column(String, default="")
    is_active = Column(Boolean, default=True)      # True = हमेशा ऑन
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def generate_key():
        return "pk_" + secrets.token_urlsafe(32)