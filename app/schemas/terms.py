from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TermsStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TermsAndConditionsBase(BaseModel):
    version: str
    title: str
    content: str
    status: TermsStatusEnum = TermsStatusEnum.DRAFT
    is_current: bool = False


class TermsAndConditionsCreate(TermsAndConditionsBase):
    pass


class TermsAndConditionsUpdate(BaseModel):
    version: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[TermsStatusEnum] = None
    is_current: Optional[bool] = None


class TermsAndConditionsResponse(TermsAndConditionsBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserTermsAgreementBase(BaseModel):
    terms_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserTermsAgreementCreate(UserTermsAgreementBase):
    pass


class UserTermsAgreementResponse(UserTermsAgreementBase):
    id: int
    user_id: int
    accepted_at: datetime
    
    class Config:
        from_attributes = True


class CurrentTermsResponse(BaseModel):
    terms: TermsAndConditionsResponse
    user_agreed: bool
    user_agreement_date: Optional[datetime] = None 