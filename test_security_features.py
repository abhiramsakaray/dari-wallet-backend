#!/usr/bin/env python3
"""
Test script to verify all security features are working correctly.
Run this script to test the implementation before deployment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.transaction import Transaction
from app.models.login_log import LoginLog
from app.services.pin import PINService
from app.services.login_logger import LoginLogger
from app.services.analytics import AnalyticsService
from app.services.transaction_history import TransactionHistoryService
from app.core.security import get_password_hash, verify_password


def test_database_models():
    """Test that all new models can be created"""
    print("Testing database models...")
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test User model with new PIN fields
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            hashed_pin=get_password_hash("1234"),
            pin_failed_attempts=0,
            pin_blocked_until=None
        )
        db.add(user)
        db.commit()
        print("✓ User model with PIN fields created successfully")
        
        # Test Transaction model with new fields
        transaction = Transaction(
            user_id=user.id,
            tx_hash="0x1234567890abcdef",
            chain="ethereum",
            from_address="0x1234567890abcdef",
            to_address="0xabcdef1234567890",
            amount=1.5,
            device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ip_address="192.168.1.1",
            location="New York, USA",
            pin_attempts=1
        )
        db.add(transaction)
        db.commit()
        print("✓ Transaction model with logging fields created successfully")
        
        # Test LoginLog model
        login_log = LoginLog(
            user_id=user.id,
            email="test@example.com",
            success=True,
            device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ip_address="192.168.1.1",
            location="New York, USA",
            country="USA",
            city="New York",
            timezone="America/New_York",
            admin_login=False
        )
        db.add(login_log)
        db.commit()
        print("✓ LoginLog model created successfully")
        
        # Clean up
        db.delete(login_log)
        db.delete(transaction)
        db.delete(user)
        db.commit()
        
    except Exception as e:
        print(f"✗ Error testing models: {e}")
        return False
    
    finally:
        db.close()
    
    return True


def test_pin_service():
    """Test PIN service functionality"""
    print("\nTesting PIN service...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            hashed_pin=get_password_hash("1234"),
            pin_failed_attempts=0,
            pin_blocked_until=None
        )
        db.add(user)
        db.commit()
        
        pin_service = PINService(db)
        
        # Test PIN verification
        result = pin_service.verify_pin(user, "1234")
        if result:
            print("✓ PIN verification successful")
        else:
            print("✗ PIN verification failed")
            return False
        
        # Test PIN status
        status = pin_service.get_pin_status(user)
        if status["pin_set"] and not status["is_blocked"]:
            print("✓ PIN status check successful")
        else:
            print("✗ PIN status check failed")
            return False
        
        # Test failed PIN attempts
        try:
            pin_service.verify_pin(user, "wrong_pin")
        except Exception as e:
            if "Invalid PIN" in str(e):
                print("✓ Failed PIN attempt handling successful")
            else:
                print(f"✗ Failed PIN attempt handling failed: {e}")
                return False
        
        # Clean up
        db.delete(user)
        db.commit()
        
    except Exception as e:
        print(f"✗ Error testing PIN service: {e}")
        return False
    
    finally:
        db.close()
    
    return True


def test_login_logger():
    """Test login logger functionality"""
    print("\nTesting login logger...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        
        login_logger = LoginLogger(db)
        
        # Test successful login logging
        log = login_logger.log_successful_login(
            user=user,
            device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ip_address="192.168.1.1",
            admin_login=False
        )
        
        if log.success and log.user_id == user.id:
            print("✓ Successful login logging working")
        else:
            print("✗ Successful login logging failed")
            return False
        
        # Test failed login logging
        log = login_logger.log_failed_login(
            email="test@example.com",
            failure_reason="wrong_password",
            device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ip_address="192.168.1.1"
        )
        
        if not log.success and log.email == "test@example.com":
            print("✓ Failed login logging working")
        else:
            print("✗ Failed login logging failed")
            return False
        
        # Test login statistics
        stats = login_logger.get_login_statistics(user.id)
        if stats["total_attempts"] >= 2:
            print("✓ Login statistics working")
        else:
            print("✗ Login statistics failed")
            return False
        
        # Clean up
        db.delete(user)
        db.commit()
        
    except Exception as e:
        print(f"✗ Error testing login logger: {e}")
        return False
    
    finally:
        db.close()
    
    return True


def test_analytics_service():
    """Test analytics service functionality"""
    print("\nTesting analytics service...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        
        # Create test transactions
        for i in range(3):
            transaction = Transaction(
                user_id=user.id,
                tx_hash=f"0x1234567890abcdef{i}",
                chain="ethereum",
                from_address="0x1234567890abcdef",
                to_address="0xabcdef1234567890",
                amount=1.5,
                device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                ip_address="192.168.1.1",
                location="New York, USA",
                pin_attempts=1
            )
            db.add(transaction)
        
        db.commit()
        
        analytics_service = AnalyticsService(db)
        
        # Test frequent transfers
        frequent_transfers = analytics_service.get_frequent_transfers(user.id)
        if isinstance(frequent_transfers, list):
            print("✓ Frequent transfers analytics working")
        else:
            print("✗ Frequent transfers analytics failed")
            return False
        
        # Test peak usage
        peak_usage = analytics_service.get_peak_usage_times(user.id)
        if "peak_hours" in peak_usage and "peak_days" in peak_usage:
            print("✓ Peak usage analytics working")
        else:
            print("✗ Peak usage analytics failed")
            return False
        
        # Test fraud indicators
        indicators = analytics_service.get_fraud_indicators(user.id)
        if "risk_score" in indicators and "fraud_indicators" in indicators:
            print("✓ Fraud indicators analytics working")
        else:
            print("✗ Fraud indicators analytics failed")
            return False
        
        # Clean up
        db.query(Transaction).filter(Transaction.user_id == user.id).delete()
        db.delete(user)
        db.commit()
        
    except Exception as e:
        print(f"✗ Error testing analytics service: {e}")
        return False
    
    finally:
        db.close()
    
    return True


def test_transaction_history_service():
    """Test transaction history service functionality"""
    print("\nTesting transaction history service...")
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        
        # Create test transactions
        for i in range(2):
            transaction = Transaction(
                user_id=user.id,
                tx_hash=f"0x1234567890abcdef{i}",
                chain="ethereum",
                from_address="0x1234567890abcdef",
                to_address="0xabcdef1234567890",
                amount=1.5,
                device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                ip_address="192.168.1.1",
                location="New York, USA",
                pin_attempts=1
            )
            db.add(transaction)
        
        db.commit()
        
        history_service = TransactionHistoryService(db)
        
        # Test comprehensive transaction history
        history = history_service.get_comprehensive_transaction_history(user.id)
        if isinstance(history, list) and len(history) >= 2:
            print("✓ Comprehensive transaction history working")
        else:
            print("✗ Comprehensive transaction history failed")
            return False
        
        # Test transaction patterns
        patterns = history_service.get_transaction_patterns(user.id)
        if "total_transactions" in patterns and "fraud_risk_score" in patterns:
            print("✓ Transaction patterns working")
        else:
            print("✗ Transaction patterns failed")
            return False
        
        # Test frequent recipients
        recipients = history_service.get_frequent_recipients(user.id)
        if isinstance(recipients, list):
            print("✓ Frequent recipients working")
        else:
            print("✗ Frequent recipients failed")
            return False
        
        # Clean up
        db.query(Transaction).filter(Transaction.user_id == user.id).delete()
        db.delete(user)
        db.commit()
        
    except Exception as e:
        print(f"✗ Error testing transaction history service: {e}")
        return False
    
    finally:
        db.close()
    
    return True


def main():
    """Run all tests"""
    print("🔍 Testing Security Features Implementation")
    print("=" * 50)
    
    tests = [
        ("Database Models", test_database_models),
        ("PIN Service", test_pin_service),
        ("Login Logger", test_login_logger),
        ("Analytics Service", test_analytics_service),
        ("Transaction History Service", test_transaction_history_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Security features are ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 