 #!/usr/bin/env python3
"""
Script to initialize default currencies in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.currency import Currency


def init_currencies():
    """Initialize default currencies"""
    db = next(get_db())
    
    # Default currencies
    default_currencies = [
        {
            "code": "USD",
            "name": "US Dollar",
            "symbol": "$",
            "is_crypto": False,
            "is_active": True
        },
        {
            "code": "EUR",
            "name": "Euro",
            "symbol": "€",
            "is_crypto": False,
            "is_active": True
        },
        {
            "code": "GBP",
            "name": "British Pound",
            "symbol": "£",
            "is_crypto": False,
            "is_active": True
        },
        {
            "code": "JPY",
            "name": "Japanese Yen",
            "symbol": "¥",
            "is_crypto": False,
            "is_active": True
        },
        {
            "code": "BTC",
            "name": "Bitcoin",
            "symbol": "₿",
            "is_crypto": True,
            "is_active": True
        },
        {
            "code": "ETH",
            "name": "Ethereum",
            "symbol": "Ξ",
            "is_crypto": True,
            "is_active": True
        },
        {
            "code": "BNB",
            "name": "Binance Coin",
            "symbol": "BNB",
            "is_crypto": True,
            "is_active": True
        },
        {
            "code": "SOL",
            "name": "Solana",
            "symbol": "◎",
            "is_crypto": True,
            "is_active": True
        },
        {
            "code": "XRP",
            "name": "Ripple",
            "symbol": "XRP",
            "is_crypto": True,
            "is_active": True
        },
        {
            "code": "TRX",
            "name": "TRON",
            "symbol": "TRX",
            "is_crypto": True,
            "is_active": True
        }
    ]
    
    try:
        # Check if currencies already exist
        existing_currencies = db.query(Currency).count()
        if existing_currencies > 0:
            print(f"Found {existing_currencies} existing currencies. Skipping initialization.")
            return
        
        # Add currencies
        for currency_data in default_currencies:
            currency = Currency(**currency_data)
            db.add(currency)
        
        db.commit()
        print(f"Successfully initialized {len(default_currencies)} currencies:")
        for currency in default_currencies:
            print(f"  - {currency['code']} ({currency['name']})")
            
    except Exception as e:
        print(f"Error initializing currencies: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_currencies()