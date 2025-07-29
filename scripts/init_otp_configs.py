#!/usr/bin/env python3
"""
Script to initialize default OTP configurations in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.otp import OTPConfig, OTPType, OTPChannel


def init_otp_configs():
    """Initialize default OTP configurations"""
    db = next(get_db())
    
    # Default OTP configurations (all disabled by default)
    default_configs = [
        {
            "name": "login_email_otp",
            "is_enabled": False,  # Disabled by default
            "otp_type": OTPType.LOGIN,
            "channel": OTPChannel.EMAIL,
            "otp_length": 6,
            "expiry_minutes": 10,
            "max_attempts": 3,
            "cooldown_minutes": 1
        },
        {
            "name": "login_sms_otp",
            "is_enabled": False,  # Disabled by default
            "otp_type": OTPType.LOGIN,
            "channel": OTPChannel.SMS,
            "otp_length": 6,
            "expiry_minutes": 10,
            "max_attempts": 3,
            "cooldown_minutes": 1
        },
        {
            "name": "email_verification_otp",
            "is_enabled": False,
            "otp_type": OTPType.EMAIL_VERIFICATION,
            "channel": OTPChannel.EMAIL,
            "otp_length": 6,
            "expiry_minutes": 15,
            "max_attempts": 3,
            "cooldown_minutes": 2
        },
        {
            "name": "password_reset_otp",
            "is_enabled": False,
            "otp_type": OTPType.PASSWORD_RESET,
            "channel": OTPChannel.EMAIL,
            "otp_length": 6,
            "expiry_minutes": 30,
            "max_attempts": 3,
            "cooldown_minutes": 5
        },
        {
            "name": "two_factor_otp",
            "is_enabled": False,
            "otp_type": OTPType.TWO_FACTOR,
            "channel": OTPChannel.EMAIL,
            "otp_length": 6,
            "expiry_minutes": 10,
            "max_attempts": 3,
            "cooldown_minutes": 1
        }
    ]
    
    try:
        # Check if configs already exist
        existing_configs = db.query(OTPConfig).count()
        if existing_configs > 0:
            print(f"Found {existing_configs} existing OTP configurations. Skipping initialization.")
            return
        
        # Add configurations
        for config_data in default_configs:
            config = OTPConfig(**config_data)
            db.add(config)
        
        db.commit()
        print(f"Successfully initialized {len(default_configs)} OTP configurations:")
        for config in default_configs:
            status = "ENABLED" if config["is_enabled"] else "DISABLED"
            print(f"  - {config['name']} ({config['otp_type'].value} - {config['channel'].value}) - {status}")
            
        print("\nNote: All OTP configurations are DISABLED by default for security.")
        print("Admins can enable them through the admin panel when ready.")
            
    except Exception as e:
        print(f"Error initializing OTP configurations: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_otp_configs() 