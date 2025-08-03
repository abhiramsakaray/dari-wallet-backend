from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    default_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    encryption_key = Column(Text)  # Encrypted user-specific encryption key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    hashed_pin = Column(String, nullable=True)  # Hashed PIN for transactions
    pin_failed_attempts = Column(Integer, default=0)  # Failed PIN attempts today
    pin_blocked_until = Column(DateTime, nullable=True)  # If set, user is blocked from transfers until this time
    
    # Foreign Keys
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    default_currency = relationship("Currency")
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    aliases = relationship("Alias", back_populates="user")
    logs = relationship("Log", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)
    otps = relationship("OTP", back_populates="user")
    login_logs = relationship("LoginLog", back_populates="user")
    terms_agreements = relationship("UserTermsAgreement", back_populates="user")
    qr_codes = relationship("QRCode", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>" 