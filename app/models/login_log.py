from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class LoginLog(Base):
    __tablename__ = "login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for failed logins
    email = Column(String, nullable=False)  # Email used in login attempt
    success = Column(Boolean, default=False)
    login_method = Column(String, default="password")  # password, otp, admin_otp
    device_info = Column(String, nullable=True)  # User agent, device type
    ip_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    failure_reason = Column(String, nullable=True)  # wrong_password, account_locked, etc.
    otp_required = Column(Boolean, default=False)
    otp_verified = Column(Boolean, default=False)
    admin_login = Column(Boolean, default=False)  # True for admin/role-based admin logins
    session_duration = Column(Integer, nullable=True)  # Session duration in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="login_logs")
    
    def __repr__(self):
        return f"<LoginLog(id={self.id}, email='{self.email}', success={self.success})>" 