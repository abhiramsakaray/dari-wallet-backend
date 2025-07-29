from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class NotificationType(enum.Enum):
    LOGIN = "login"
    TRANSFER_SENT = "transfer_sent"
    TRANSFER_RECEIVED = "transfer_received"
    PROMOTION = "promotion"
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"
    WALLET_CREATED = "wallet_created"
    ALIAS_CREATED = "alias_created"
    VERIFICATION = "verification"


class NotificationChannel(enum.Enum):
    APP = "app"
    EMAIL = "email"
    SMS = "sms"


class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    read_at = Column(DateTime)
    sent_at = Column(DateTime)
    failed_at = Column(DateTime)
    error_message = Column(Text)
    notification_metadata = Column(Text)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type.value}', user_id={self.user_id})>"


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    title_template = Column(String, nullable=False)
    message_template = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationTemplate(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    app_enabled = Column(Boolean, default=True)
    login_notifications = Column(Boolean, default=True)
    transfer_notifications = Column(Boolean, default=True)
    promotion_notifications = Column(Boolean, default=True)
    security_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notification_settings")
    
    def __repr__(self):
        return f"<NotificationSettings(id={self.id}, user_id={self.user_id})>" 