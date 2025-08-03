from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.otp import OTPService
from app.services.pin import PINService
from app.core.security import get_password_hash
from app.schemas.otp import OTPVerify
from app.schemas.pin import PINStatusResponse

router = APIRouter(prefix="/pin", tags=["PIN Management"])

@router.post("/set")
def set_pin(
    otp_verify: OTPVerify,
    pin: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set a new PIN (OTP verification temporarily disabled)"""
    # OTP verification is disabled for now
    current_user.hashed_pin = get_password_hash(pin)
    current_user.pin_failed_attempts = 0
    current_user.pin_blocked_until = None
    db.commit()
    return {"message": "PIN set successfully (OTP not required)"}

@router.post("/reset")
def reset_pin(
    otp_verify: OTPVerify,
    pin: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reset PIN (OTP verification temporarily disabled)"""
    # OTP verification is disabled for now
    current_user.hashed_pin = get_password_hash(pin)
    current_user.pin_failed_attempts = 0
    current_user.pin_blocked_until = None
    db.commit()
    return {"message": "PIN reset successfully (OTP not required)"}


@router.get("/status", response_model=PINStatusResponse)
def get_pin_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's PIN status"""
    pin_service = PINService(db)
    status = pin_service.get_pin_status(current_user)
    # Ensure is_blocked is always a boolean
    status["is_blocked"] = bool(status.get("is_blocked", False))
    return PINStatusResponse(**status)
    # To setup mail for OTP, configure SMTP settings in your .env and use a mail sending function in OTPService.