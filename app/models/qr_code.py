from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    qr_type = Column(String, nullable=False)  # 'receive', 'payment', etc.
    qr_data = Column(Text, nullable=False)  # JSON data for QR code
    qr_image = Column(LargeBinary, nullable=False)  # PNG image data
    amount = Column(String, nullable=True)  # Amount if specified
    memo = Column(String, nullable=True)  # Memo if specified
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    # Relationships
    user = relationship("User", back_populates="qr_codes")
    wallet = relationship("Wallet", back_populates="qr_codes")
    
    def __repr__(self):
        return f"<QRCode(id={self.id}, user_id={self.user_id}, qr_type='{self.qr_type}')>" 