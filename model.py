from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import secrets

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    base_url = Column(String, default="https://api.openai.com/v1")
    model_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ProductKey(Base):
    __tablename__ = "product_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, default="Company Product")
    company_name = Column(String, default="")
    
    # 20+ words (Low), 50+ words (Medium), 100+ words (Hard) Mappings
    low_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    medium_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    hard_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    low_provider = relationship("Provider", foreign_keys=[low_provider_id])
    medium_provider = relationship("Provider", foreign_keys=[medium_provider_id])
    hard_provider = relationship("Provider", foreign_keys=[hard_provider_id])

    @staticmethod
    def generate_key():
        return "pk_" + secrets.token_urlsafe(32)
