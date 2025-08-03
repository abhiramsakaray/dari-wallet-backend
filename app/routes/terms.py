from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.models.terms import TermsAndConditions, UserTermsAgreement, TermsStatus
from app.schemas.terms import (
    TermsAndConditionsCreate, TermsAndConditionsUpdate, TermsAndConditionsResponse,
    UserTermsAgreementCreate, UserTermsAgreementResponse, CurrentTermsResponse
)

router = APIRouter(prefix="/terms", tags=["Terms and Conditions"])


@router.get("/current", response_model=CurrentTermsResponse)
def get_current_terms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current active terms and conditions and user's agreement status"""
    # Get current active terms
    current_terms = db.query(TermsAndConditions).filter(
        TermsAndConditions.status == TermsStatus.ACTIVE,
        TermsAndConditions.is_current == True
    ).first()
    
    if not current_terms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active terms and conditions found"
        )
    
    # Check if user has agreed to current terms
    user_agreement = db.query(UserTermsAgreement).filter(
        UserTermsAgreement.user_id == current_user.id,
        UserTermsAgreement.terms_id == current_terms.id
    ).first()
    
    return CurrentTermsResponse(
        terms=current_terms,
        user_agreed=user_agreement is not None,
        user_agreement_date=user_agreement.accepted_at if user_agreement else None
    )


@router.post("/agree", response_model=UserTermsAgreementResponse)
def agree_to_terms(
    agreement: UserTermsAgreementCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Agree to current terms and conditions"""
    # Verify terms exist
    terms = db.query(TermsAndConditions).filter(
        TermsAndConditions.id == agreement.terms_id,
        TermsAndConditions.status == TermsStatus.ACTIVE
    ).first()
    
    if not terms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terms and conditions not found or not active"
        )
    
    # Check if user already agreed
    existing_agreement = db.query(UserTermsAgreement).filter(
        UserTermsAgreement.user_id == current_user.id,
        UserTermsAgreement.terms_id == agreement.terms_id
    ).first()
    
    if existing_agreement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already agreed to these terms"
        )
    
    # Create agreement
    user_agreement = UserTermsAgreement(
        user_id=current_user.id,
        terms_id=agreement.terms_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(user_agreement)
    db.commit()
    db.refresh(user_agreement)
    
    return user_agreement


# Admin routes
@router.post("/", response_model=TermsAndConditionsResponse)
def create_terms(
    terms_data: TermsAndConditionsCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new terms and conditions (admin only)"""
    # If this is set as current, deactivate others
    if terms_data.is_current:
        db.query(TermsAndConditions).filter(
            TermsAndConditions.is_current == True
        ).update({"is_current": False})
    
    terms = TermsAndConditions(
        **terms_data.dict(),
        created_by=current_user.id
    )
    
    db.add(terms)
    db.commit()
    db.refresh(terms)
    
    return terms


@router.get("/", response_model=List[TermsAndConditionsResponse])
def get_all_terms(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all terms and conditions (admin only)"""
    terms = db.query(TermsAndConditions).order_by(TermsAndConditions.created_at.desc()).all()
    return terms


@router.get("/{terms_id}", response_model=TermsAndConditionsResponse)
def get_terms_by_id(
    terms_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get specific terms and conditions (admin only)"""
    terms = db.query(TermsAndConditions).filter(TermsAndConditions.id == terms_id).first()
    if not terms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terms and conditions not found"
        )
    return terms


@router.put("/{terms_id}", response_model=TermsAndConditionsResponse)
def update_terms(
    terms_id: int,
    terms_data: TermsAndConditionsUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update terms and conditions (admin only)"""
    terms = db.query(TermsAndConditions).filter(TermsAndConditions.id == terms_id).first()
    if not terms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terms and conditions not found"
        )
    
    # If setting as current, deactivate others
    if terms_data.is_current:
        db.query(TermsAndConditions).filter(
            TermsAndConditions.is_current == True
        ).update({"is_current": False})
    
    # Update fields
    for field, value in terms_data.dict(exclude_unset=True).items():
        setattr(terms, field, value)
    
    db.commit()
    db.refresh(terms)
    
    return terms


@router.delete("/{terms_id}")
def delete_terms(
    terms_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete terms and conditions (admin only)"""
    terms = db.query(TermsAndConditions).filter(TermsAndConditions.id == terms_id).first()
    if not terms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terms and conditions not found"
        )
    
    # Check if any users have agreed to these terms
    agreements = db.query(UserTermsAgreement).filter(
        UserTermsAgreement.terms_id == terms_id
    ).count()
    
    if agreements > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete terms that users have agreed to"
        )
    
    db.delete(terms)
    db.commit()
    
    return {"message": "Terms and conditions deleted successfully"} 