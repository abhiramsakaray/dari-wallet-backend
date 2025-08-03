from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Synchronous database
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous database
async_engine = create_async_engine(settings.async_database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Import all models so they are registered with Base
from app.models.user import User
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.role import Role
from app.models.token import Token
from app.models.token_balance import TokenBalance
from app.models.alias import Alias
from app.models.log import Log
from app.models.currency import Currency
from app.models.notification import Notification, NotificationTemplate, NotificationSettings, NotificationType, NotificationChannel, NotificationStatus
from app.models.otp import OTP, OTPConfig, OTPType, OTPChannel, OTPStatus
from app.models.login_log import LoginLog
from app.models.terms import TermsAndConditions, UserTermsAgreement
from app.models.qr_code import QRCode
# ...import any other models you have


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 