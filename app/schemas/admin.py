from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_transactions: int
    total_volume_usd: Decimal
    total_wallets: int
    chains_supported: List[str]


class UserAdminResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    last_login: Optional[datetime]
    wallet_count: int
    transaction_count: int
    
    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['user', 'admin', 'support']
        if v not in valid_roles:
            raise ValueError(f'Invalid role. Valid roles: {valid_roles}')
        return v


class TokenAdd(BaseModel):
    chain: str
    symbol: str
    name: str
    contract_address: Optional[str] = None
    decimals: int = 18
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    @validator('chain')
    def validate_chain(cls, v):
        supported_chains = ['ethereum', 'bsc', 'tron', 'solana', 'bitcoin', 'xrp']
        if v.lower() not in supported_chains:
            raise ValueError(f'Unsupported chain. Supported chains: {supported_chains}')
        return v.lower()


class SystemLog(BaseModel):
    id: int
    level: str
    category: str
    message: str
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    user_id: Optional[int]
    
    class Config:
        from_attributes = True


class BroadcastMessage(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, warning, error, success
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['info', 'warning', 'error', 'success']
        if v not in valid_types:
            raise ValueError(f'Invalid type. Valid types: {valid_types}')
        return v


class RPCConfig(BaseModel):
    chain: str
    rpc_url: str
    api_key: Optional[str] = None
    
    @validator('chain')
    def validate_chain(cls, v):
        supported_chains = ['ethereum', 'bsc', 'tron', 'solana', 'bitcoin', 'xrp']
        if v.lower() not in supported_chains:
            raise ValueError(f'Unsupported chain. Supported chains: {supported_chains}')
        return v.lower() 