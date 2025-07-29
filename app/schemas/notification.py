from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationTypeEnum(str, Enum):
    LOGIN = "login"
    TRANSFER_SENT = "transfer_sent"
    TRANSFER_RECEIVED = "transfer_received"
    PROMOTION = "promotion"
    SECURITY_ALERT = "security_alert"
    SYSTEM_UPDATE = "system_update"
    WALLET_CREATED = "wallet_created"
    ALIAS_CREATED = "alias_created"
    VERIFICATION = "verification"


class NotificationChannelEnum(str, Enum):
    APP = "app"
    EMAIL = "email"
    SMS = "sms"


class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


# Notification Schemas
class NotificationBase(BaseModel):
    type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatusEnum
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatusEnum] = None
    read_at: Optional[datetime] = None


# Notification Template Schemas
class NotificationTemplateBase(BaseModel):
    name: str
    type: NotificationTypeEnum
    channel: NotificationChannelEnum
    title_template: str
    message_template: str
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[NotificationTypeEnum] = None
    channel: Optional[NotificationChannelEnum] = None
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Notification Settings Schemas
class NotificationSettingsBase(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    app_enabled: bool = True
    login_notifications: bool = True
    transfer_notifications: bool = True
    promotion_notifications: bool = True
    security_notifications: bool = True
    system_notifications: bool = True


class NotificationSettingsCreate(NotificationSettingsBase):
    user_id: int


class NotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    app_enabled: Optional[bool] = None
    login_notifications: Optional[bool] = None
    transfer_notifications: Optional[bool] = None
    promotion_notifications: Optional[bool] = None
    security_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None


class NotificationSettingsResponse(NotificationSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Notification List Schemas
class NotificationList(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationTemplateList(BaseModel):
    templates: list[NotificationTemplateResponse]
    total: int 