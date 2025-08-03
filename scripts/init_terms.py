#!/usr/bin/env python3
"""
Initialize Terms and Conditions for DARI Wallet Backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.terms import TermsAndConditions, TermsStatus
from app.models.user import User


def init_terms_and_conditions():
    """Initialize default terms and conditions"""
    db = SessionLocal()
    
    try:
        # Check if terms already exist
        existing_terms = db.query(TermsAndConditions).filter(
            TermsAndConditions.is_current == True
        ).first()
        
        if existing_terms:
            print("Terms and conditions already exist. Skipping initialization.")
            return
        
        # Get admin user
        admin_user = db.query(User).filter(User.email == "admin@dari.com").first()
        if not admin_user:
            print("Admin user not found. Please run init_db.py first.")
            return
        
        # Read terms from file
        terms_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TERMS_AND_CONDITIONS.md")
        
        if not os.path.exists(terms_file_path):
            print(f"Terms file not found at {terms_file_path}")
            return
        
        with open(terms_file_path, 'r', encoding='utf-8') as f:
            terms_content = f.read()
        
        # Create terms and conditions
        terms = TermsAndConditions(
            version="1.0",
            title="DARI Wallet Terms and Conditions",
            content=terms_content,
            status=TermsStatus.ACTIVE,
            is_current=True,
            created_by=admin_user.id
        )
        
        db.add(terms)
        db.commit()
        
        print("Successfully initialized Terms and Conditions:")
        print(f"  - Version: {terms.version}")
        print(f"  - Title: {terms.title}")
        print(f"  - Status: {terms.status.value}")
        print(f"  - Created by: {admin_user.email}")
        
    except Exception as e:
        print(f"Error initializing terms and conditions: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing DARI Wallet Terms and Conditions...")
    init_terms_and_conditions() 