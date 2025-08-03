from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class OTPTypeEnum(str, Enum):
    LOGIN = "login"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    TWO_FACTOR = "two_factor"


class OTPChannelEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"


class OTPStatusEnum(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"
    FAILED = "failed"


# OTP Request/Response Schemas
class OTPRequest(BaseModel):
    email: str
    otp_type: OTPTypeEnum = OTPTypeEnum.LOGIN
    channel: OTPChannelEnum = OTPChannelEnum.EMAIL


class OTPVerify(BaseModel):
    email: Optional[str] = None
    otp_code: Optional[str] = None
    otp_type: OTPTypeEnum = OTPTypeEnum.LOGIN


class OTPResponse(BaseModel):
    message: str
    expires_in_minutes: int
    can_resend_in_minutes: int


class OTPVerifyResponse(BaseModel):
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


# OTP Configuration Schemas
class OTPConfigBase(BaseModel):
    name: str
    is_enabled: bool = False
    otp_type: OTPTypeEnum
    channel: OTPChannelEnum
    otp_length: int = 6
    expiry_minutes: int = 10
    max_attempts: int = 3
    cooldown_minutes: int = 1
    
    @validator('otp_length')
    def validate_otp_length(cls, v):
        if v < 4 or v > 8:
            raise ValueError('OTP length must be between 4 and 8 digits')
        return v
    
    @validator('expiry_minutes')
    def validate_expiry_minutes(cls, v):
        if v < 1 or v > 60:
            raise ValueError('Expiry minutes must be between 1 and 60')
        return v
    
    @validator('max_attempts')
    def validate_max_attempts(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Max attempts must be between 1 and 10')
        return v


class OTPConfigCreate(OTPConfigBase):
    pass


class OTPConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    otp_length: Optional[int] = None
    expiry_minutes: Optional[int] = None
    max_attempts: Optional[int] = None
    cooldown_minutes: Optional[int] = None
    
    @validator('otp_length')
    def validate_otp_length(cls, v):
        if v is not None and (v < 4 or v > 8):
            raise ValueError('OTP length must be between 4 and 8 digits')
        return v
    
    @validator('expiry_minutes')
    def validate_expiry_minutes(cls, v):
        if v is not None and (v < 1 or v > 60):
            raise ValueError('Expiry minutes must be between 1 and 60')
        return v
    
    @validator('max_attempts')
    def validate_max_attempts(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Max attempts must be between 1 and 10')
        return v


class OTPConfigResponse(OTPConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OTPConfigList(BaseModel):
    configs: list[OTPConfigResponse]
    total: int 