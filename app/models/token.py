from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    chain = Column(String, nullable=False)  # ethereum, bsc, tron, solana, bitcoin, xrp
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    contract_address = Column(String, index=True)  # For ERC20/TRC20/SPL tokens
    decimals = Column(Integer, default=18)
    total_supply = Column(Numeric(30, 0))
    price_usd = Column(Numeric(20, 8))
    market_cap = Column(Numeric(20, 2))
    volume_24h = Column(Numeric(20, 2))
    is_active = Column(Boolean, default=True)
    is_native = Column(Boolean, default=False)  # True for native tokens like ETH, BNB, etc.
    logo_url = Column(String)
    website = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    token_balances = relationship("TokenBalance", back_populates="token")
    transactions = relationship("Transaction", back_populates="token")
    
    def __repr__(self):
        return f"<Token(id={self.id}, chain='{self.chain}', symbol='{self.symbol}')>" 