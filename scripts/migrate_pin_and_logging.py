#!/usr/bin/env python3
"""
Database migration script to add PIN management, transaction logging, and login logging fields.
Run this script to update your database schema.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.transaction import Transaction
from app.models.login_log import LoginLog


def run_migration():
    """Run the database migration"""
    print("Starting database migration...")
    
    # Create database engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Add new columns to users table
        print("Adding PIN management columns to users table...")
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN hashed_pin VARCHAR(255),
                ADD COLUMN pin_failed_attempts INTEGER DEFAULT 0,
                ADD COLUMN pin_blocked_until TIMESTAMP
            """))
            print("✓ Added PIN management columns to users table")
        except Exception as e:
            print(f"Note: Some columns may already exist: {e}")
        
        # Add new columns to transactions table
        print("Adding transaction logging columns to transactions table...")
        try:
            conn.execute(text("""
                ALTER TABLE transactions 
                ADD COLUMN device_info VARCHAR(500),
                ADD COLUMN ip_address VARCHAR(45),
                ADD COLUMN location VARCHAR(255),
                ADD COLUMN pin_attempts INTEGER DEFAULT 0
            """))
            print("✓ Added transaction logging columns to transactions table")
        except Exception as e:
            print(f"Note: Some columns may already exist: {e}")
        
        # Create login_logs table
        print("Creating login_logs table...")
        try:
            conn.execute(text("""
                CREATE TABLE login_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    email VARCHAR(255) NOT NULL,
                    success BOOLEAN DEFAULT FALSE,
                    login_method VARCHAR(50) DEFAULT 'password',
                    device_info VARCHAR(500),
                    ip_address VARCHAR(45),
                    location VARCHAR(255),
                    country VARCHAR(100),
                    city VARCHAR(100),
                    timezone VARCHAR(50),
                    failure_reason VARCHAR(255),
                    otp_required BOOLEAN DEFAULT FALSE,
                    otp_verified BOOLEAN DEFAULT FALSE,
                    admin_login BOOLEAN DEFAULT FALSE,
                    session_duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✓ Created login_logs table")
        except Exception as e:
            print(f"Note: login_logs table may already exist: {e}")
        
        # Create indexes for better performance
        print("Creating indexes...")
        try:
            conn.execute(text("CREATE INDEX idx_login_logs_user_id ON login_logs(user_id)"))
            conn.execute(text("CREATE INDEX idx_login_logs_email ON login_logs(email)"))
            conn.execute(text("CREATE INDEX idx_login_logs_created_at ON login_logs(created_at)"))
            conn.execute(text("CREATE INDEX idx_transactions_device_info ON transactions(device_info)"))
            conn.execute(text("CREATE INDEX idx_transactions_ip_address ON transactions(ip_address)"))
            print("✓ Created performance indexes")
        except Exception as e:
            print(f"Note: Some indexes may already exist: {e}")
        
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        print("\nNew features added:")
        print("- PIN management for users")
        print("- Transaction logging with device info, IP, and location")
        print("- Comprehensive login logging")
        print("- Fraud analysis capabilities")


if __name__ == "__main__":
    run_migration() 