from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/dari_wallet"
    async_database_url: str = "postgresql+asyncpg://username:password@localhost:5432/dari_wallet"
    
    # Security
    secret_key: str = "your-secret-key-here-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Blockchain RPC URLs
    ethereum_rpc_url: str = "https://mainnet.infura.io/v3/your-project-id"
    bsc_rpc_url: str = "https://bsc-dataseed1.binance.org"
    tron_rpc_url: str = "https://api.trongrid.io"
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    bitcoin_rpc_url: str = "http://localhost:8332"
    xrp_rpc_url: str = "https://s1.ripple.com:51234"
    
    # Third-party API Keys
    coingecko_api_key: Optional[str] = None
    coinmarketcap_api_key: Optional[str] = None
    etherscan_api_key: Optional[str] = None
    bscscan_api_key: Optional[str] = None
    tronscan_api_key: Optional[str] = None
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # SMS Configuration
    sms_api_key: Optional[str] = None
    sms_api_url: Optional[str] = None
    
    # Telegram Configuration
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/dari_wallet.log"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "https://your-frontend-domain.com"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 