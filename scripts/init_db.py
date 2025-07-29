#!/usr/bin/env python3
"""
Database initialization script for DARI Wallet Backend
Creates initial roles and admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.models.token import Token
from app.core.config import settings


def init_database():
    """Initialize database with default data"""
    db = SessionLocal()
    
    try:
        # Create roles
        roles = [
            {"name": "user", "description": "Regular user"},
            {"name": "admin", "description": "Administrator"},
            {"name": "support", "description": "Support staff"}
        ]
        
        for role_data in roles:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                print(f"Created role: {role_data['name']}")
        
        db.commit()
        
        # Create admin user if it doesn't exist
        admin_email = "admin@dari.com"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_user:
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user = User(
                    email=admin_email,
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    full_name="System Administrator",
                    role_id=admin_role.id,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                print("Created admin user: admin@dari.com / admin123")
        
        # Create default tokens for each chain
        default_tokens = [
            # Ethereum
            {"chain": "ethereum", "symbol": "ETH", "name": "Ethereum", "is_native": True, "decimals": 18},
            {"chain": "ethereum", "symbol": "USDT", "name": "Tether USD", "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "decimals": 6},
            {"chain": "ethereum", "symbol": "USDC", "name": "USD Coin", "contract_address": "0xA0b86a33E6441b8B4b8B4b8B4b8B4b8B4b8B4b8", "decimals": 6},
            
            # BSC
            {"chain": "bsc", "symbol": "BNB", "name": "Binance Coin", "is_native": True, "decimals": 18},
            {"chain": "bsc", "symbol": "BUSD", "name": "Binance USD", "contract_address": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56", "decimals": 18},
            
            # Tron
            {"chain": "tron", "symbol": "TRX", "name": "TRON", "is_native": True, "decimals": 6},
            {"chain": "tron", "symbol": "USDT", "name": "Tether USD", "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "decimals": 6},
            
            # Solana
            {"chain": "solana", "symbol": "SOL", "name": "Solana", "is_native": True, "decimals": 9},
            
            # Bitcoin
            {"chain": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "is_native": True, "decimals": 8},
            
            # XRP
            {"chain": "xrp", "symbol": "XRP", "name": "XRP", "is_native": True, "decimals": 6}
        ]
        
        for token_data in default_tokens:
            existing_token = db.query(Token).filter(
                Token.chain == token_data["chain"],
                Token.symbol == token_data["symbol"]
            ).first()
            
            if not existing_token:
                token = Token(**token_data)
                db.add(token)
                print(f"Created token: {token_data['symbol']} on {token_data['chain']}")
        
        db.commit()
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing DARI Wallet Backend database...")
    init_database() 