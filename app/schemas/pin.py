from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PINVerifyRequest(BaseModel):
    pin: str


class PINVerifyResponse(BaseModel):
    success: bool
    message: str


class PINStatusResponse(BaseModel):
    pin_set: bool
    is_blocked: bool
    blocked_until: Optional[str] = None
    failed_attempts: int
    remaining_attempts: int


class TransactionWithPIN(BaseModel):
    pin: str
    # Add other transaction fields as needed 