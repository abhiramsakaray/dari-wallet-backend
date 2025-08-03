from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Alias(Base):
    __tablename__ = "aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, default="@dari")  # Default domain, can be changed by admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="aliases")
    wallet_aliases = relationship("WalletAlias", back_populates="alias")
    
    def __repr__(self):
        return f"<Alias(id={self.id}, username='{self.username}')>"


class WalletAlias(Base):
    __tablename__ = "wallet_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    chain = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)  # Primary wallet for this chain
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    alias_id = Column(Integer, ForeignKey("aliases.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    
    # Relationships
    alias = relationship("Alias", back_populates="wallet_aliases")
    wallet = relationship("Wallet")
    
    def __repr__(self):
        return f"<WalletAlias(id={self.id}, chain='{self.chain}', is_primary={self.is_primary})>" 