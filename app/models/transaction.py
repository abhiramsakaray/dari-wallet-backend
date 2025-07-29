from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String, unique=True, index=True, nullable=False)
    chain = Column(String, nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    amount = Column(Numeric(30, 8), nullable=False)
    gas_price = Column(Numeric(20, 8))
    gas_used = Column(Numeric(20, 8))
    gas_limit = Column(Numeric(20, 8))
    fee = Column(Numeric(20, 8))
    block_number = Column(Integer)
    block_hash = Column(String)
    nonce = Column(Integer)
    status = Column(String, default="pending")  # pending, confirmed, failed
    is_incoming = Column(Boolean, default=False)
    memo = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime)
    device_info = Column(String, nullable=True)  # Device information for fraud analysis
    ip_address = Column(String, nullable=True)  # IP address for fraud analysis
    location = Column(String, nullable=True)  # Location for fraud analysis
    pin_attempts = Column(Integer, default=0)  # Number of PIN attempts for this transaction
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"))  # Null for native token transfers
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    wallet = relationship("Wallet", back_populates="transactions")
    token = relationship("Token", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, tx_hash='{self.tx_hash}', status='{self.status}')>" 