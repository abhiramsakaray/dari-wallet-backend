from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TokenBalance(Base):
    __tablename__ = "token_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric(30, 8), default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="token_balances")
    token = relationship("Token", back_populates="token_balances")
    
    def __repr__(self):
        return f"<TokenBalance(id={self.id}, balance={self.balance})>" 