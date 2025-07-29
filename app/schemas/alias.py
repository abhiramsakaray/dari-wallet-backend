from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class AliasCreate(BaseModel):
    username: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional underscores and hyphens')
        if len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be between 3 and 30 characters')
        return v.lower()


class AliasResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WalletAliasResponse(BaseModel):
    chain: str
    address: str
    is_primary: bool


class AliasResolveResponse(BaseModel):
    username: str
    wallets: List[WalletAliasResponse]
    is_verified: bool


class AliasUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None 