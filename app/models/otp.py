from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from app.core.database import Base


class OTPType(enum.Enum):
    LOGIN = "login"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR = "two_factor"


class OTPChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class OTPStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"


class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)  # 6-digit OTP
    otp_type = Column(Enum(OTPType), nullable=False)
    channel = Column(Enum(OTPChannel), nullable=False)
    status = Column(Enum(OTPStatus), default=OTPStatus.PENDING)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="otps")
    
    def __repr__(self):
        return f"<OTP(id={self.id}, user_id={self.user_id}, type='{self.otp_type.value}')>"
    
    @property
    def is_expired(self):
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if OTP is valid (not expired and not verified)"""
        return (
            self.status == OTPStatus.PENDING and 
            not self.is_expired and 
            self.attempts < self.max_attempts
        )


class OTPConfig(Base):
    __tablename__ = "otp_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False)
    otp_type = Column(Enum(OTPType), nullable=False)
    channel = Column(Enum(OTPChannel), nullable=False)
    otp_length = Column(Integer, default=6)
    expiry_minutes = Column(Integer, default=10)
    max_attempts = Column(Integer, default=3)
    cooldown_minutes = Column(Integer, default=1)  # Time between OTP requests
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<OTPConfig(id={self.id}, name='{self.name}', enabled={self.is_enabled})>" 