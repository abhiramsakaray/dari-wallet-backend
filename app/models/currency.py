from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class Currency(Base):
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)  # USD, EUR, BTC, etc.
    name = Column(String, nullable=False)  # US Dollar, Euro, Bitcoin, etc.
    symbol = Column(String(10), nullable=False)  # $, €, ₿, etc.
    is_crypto = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Currency(id={self.id}, code='{self.code}', name='{self.name}')>" 