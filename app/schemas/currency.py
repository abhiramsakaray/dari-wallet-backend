from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str
    is_crypto: bool = False
    is_active: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    is_crypto: Optional[bool] = None
    is_active: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CurrencyList(BaseModel):
    currencies: list[CurrencyResponse]
    total: int 