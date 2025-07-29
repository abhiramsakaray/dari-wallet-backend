from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class WalletCreate(BaseModel):
    chain: str
    
    @validator('chain')
    def validate_chain(cls, v):
        supported_chains = ['ethereum', 'bsc', 'tron', 'solana', 'bitcoin', 'xrp']
        if v.lower() not in supported_chains:
            raise ValueError(f'Unsupported chain. Supported chains: {supported_chains}')
        return v.lower()


class WalletResponse(BaseModel):
    id: int
    chain: str
    address: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    last_sync: Optional[datetime]
    
    class Config:
        from_attributes = True


class WalletBalance(BaseModel):
    chain: str
    address: str
    balance: Decimal
    symbol: str
    price_usd: Optional[Decimal]
    value_usd: Optional[Decimal]


class WalletExport(BaseModel):
    chain: str
    address: str
    public_key: Optional[str]
    created_at: datetime


class TransactionCreate(BaseModel):
    chain: str
    to_address: str
    amount: Decimal
    token_symbol: Optional[str] = None  # None for native token
    gas_price: Optional[Decimal] = None
    gas_limit: Optional[int] = None
    memo: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v
    
    @validator('to_address')
    def validate_address(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid address format')
        return v


class TransactionResponse(BaseModel):
    id: int
    tx_hash: str
    chain: str
    from_address: str
    to_address: str
    amount: Decimal
    gas_price: Optional[Decimal]
    gas_used: Optional[Decimal]
    gas_limit: Optional[Decimal]
    fee: Optional[Decimal]
    block_number: Optional[int]
    status: str
    is_incoming: bool
    memo: Optional[str]
    token_symbol: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenTransfer(BaseModel):
    chain: str
    to_address: str
    token_symbol: str
    amount: Decimal
    gas_price: Optional[Decimal] = None
    gas_limit: Optional[int] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v


class TokenBalance(BaseModel):
    symbol: str
    name: str
    balance: Decimal
    decimals: int
    price_usd: Optional[Decimal]
    value_usd: Optional[Decimal]
    contract_address: Optional[str]
    logo_url: Optional[str]


class GasEstimate(BaseModel):
    gas_price: Decimal
    gas_limit: int
    estimated_fee: Decimal
    max_priority_fee: Optional[Decimal] = None


class QRCodeResponse(BaseModel):
    qr_code: str  # Base64 encoded QR code image
    address: str
    amount: Optional[Decimal] = None
    memo: Optional[str] = None


class QRCodeScan(BaseModel):
    qr_data: str  # QR code data to scan and decode 