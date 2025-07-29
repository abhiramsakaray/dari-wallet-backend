from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User
from app.core.security import verify_password
from fastapi import HTTPException, status


class PINService:
    def __init__(self, db: Session):
        self.db = db
        self.max_failed_attempts = 10
        self.block_duration_hours = 24

    def verify_pin(self, user: User, pin: str) -> bool:
        """Verify user's PIN and handle failed attempts"""
        # Check if user is blocked
        if user.pin_blocked_until and user.pin_blocked_until > datetime.utcnow():
            remaining_time = user.pin_blocked_until - datetime.utcnow()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account blocked due to too many failed PIN attempts. Try again in {hours}h {minutes}m"
            )

        # Reset failed attempts if it's a new day
        if user.pin_failed_attempts > 0:
            # Check if it's a new day (simplified logic)
            # In production, you might want to track the date of failed attempts
            pass

        # Verify PIN
        if not user.hashed_pin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN not set. Please set a PIN first."
            )

        if verify_password(pin, user.hashed_pin):
            # Successful verification - reset failed attempts
            user.pin_failed_attempts = 0
            user.pin_blocked_until = None
            self.db.commit()
            return True
        else:
            # Failed verification - increment failed attempts
            user.pin_failed_attempts += 1
            
            # Check if user should be blocked
            if user.pin_failed_attempts >= self.max_failed_attempts:
                user.pin_blocked_until = datetime.utcnow() + timedelta(hours=self.block_duration_hours)
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Too many failed PIN attempts. Account blocked for {self.block_duration_hours} hours."
                )
            
            self.db.commit()
            remaining_attempts = self.max_failed_attempts - user.pin_failed_attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid PIN. {remaining_attempts} attempts remaining."
            )

    def unblock_user(self, user: User) -> bool:
        """Unblock a user (admin function)"""
        user.pin_failed_attempts = 0
        user.pin_blocked_until = None
        self.db.commit()
        return True

    def get_pin_status(self, user: User) -> dict:
        """Get user's PIN status"""
        is_blocked = user.pin_blocked_until and user.pin_blocked_until > datetime.utcnow()
        remaining_attempts = max(0, self.max_failed_attempts - user.pin_failed_attempts)
        
        return {
            "pin_set": bool(user.hashed_pin),
            "is_blocked": is_blocked,
            "blocked_until": user.pin_blocked_until.isoformat() if user.pin_blocked_until else None,
            "failed_attempts": user.pin_failed_attempts,
            "remaining_attempts": remaining_attempts
        } 