from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    chain = Column(String, nullable=False)  # ethereum, bsc, tron, solana, bitcoin, xrp
    address = Column(String, nullable=False, index=True)
    encrypted_private_key = Column(Text, nullable=False)  # Encrypted private key
    public_key = Column(String)
    mnemonic_phrase = Column(Text)  # Encrypted mnemonic phrase
    balance = Column(Numeric(20, 8), default=0)  # Native token balance
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    token_balances = relationship("TokenBalance", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, chain='{self.chain}', address='{self.address}')>" 