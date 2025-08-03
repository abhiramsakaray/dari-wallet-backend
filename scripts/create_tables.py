#!/usr/bin/env python3
"""
Database table creation script for DARI Wallet Backend
Creates all tables defined in the models
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.user import User
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.role import Role
from app.models.token import Token
from app.models.token_balance import TokenBalance
from app.models.alias import Alias
from app.models.log import Log
from app.models.currency import Currency
from app.models.notification import Notification, NotificationTemplate, NotificationSettings
from app.models.otp import OTP, OTPConfig
from app.models.login_log import LoginLog


def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


if __name__ == "__main__":
    print("Creating DARI Wallet Backend database tables...")
    create_tables() 