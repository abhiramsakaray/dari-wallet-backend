from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyUpdate, CurrencyResponse, CurrencyList

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.get("/", response_model=CurrencyList)
def get_currencies(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all currencies with pagination"""
    query = db.query(Currency)
    
    if active_only:
        query = query.filter(Currency.is_active == True)
    
    total = query.count()
    currencies = query.offset(skip).limit(limit).all()
    
    return CurrencyList(
        currencies=currencies,
        total=total
    )


@router.get("/{currency_id}", response_model=CurrencyResponse)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    """Get a specific currency by ID"""
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found"
        )
    return currency


@router.post("/", response_model=CurrencyResponse)
def create_currency(
    currency_data: CurrencyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new currency (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if currency code already exists
    existing_currency = db.query(Currency).filter(Currency.code == currency_data.code).first()
    if existing_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code already exists"
        )
    
    currency = Currency(**currency_data.dict())
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@router.put("/{currency_id}", response_model=CurrencyResponse)
def update_currency(
    currency_id: int,
    currency_data: CurrencyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a currency (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found"
        )
    
    for key, value in currency_data.dict(exclude_unset=True).items():
        setattr(currency, key, value)
    
    db.commit()
    db.refresh(currency)
    return currency


@router.delete("/{currency_id}")
def delete_currency(
    currency_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a currency (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found"
        )
    
    # Check if currency is being used by any users
    users_with_currency = db.query(User).filter(User.default_currency_id == currency_id).count()
    if users_with_currency > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete currency that is being used by users"
        )
    
    db.delete(currency)
    db.commit()
    
    return {"message": "Currency deleted successfully"} 