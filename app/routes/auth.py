from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, UserUpdate, PasswordChange
from app.services.login_logger import LoginLogger
from app.services.otp import OTPService
from typing import List, Union
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate default currency if provided
    if user_data.default_currency_id:
        from app.models.currency import Currency
        currency = db.query(Currency).filter(Currency.id == user_data.default_currency_id).first()
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid default currency"
            )
    
    # Get default user role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user role not found"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        default_currency_id=user_data.default_currency_id,
        role_id=user_role.id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.post("/login")  # Remove response_model=Token for now
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return tokens"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    # Get device info and IP for logging
    device_info = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    login_logger = LoginLogger(db)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        # Log failed login attempt
        login_logger.log_failed_login(
            email=user_data.email,
            failure_reason="wrong_password",
            device_info=device_info,
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        # Log failed login attempt
        login_logger.log_failed_login(
            email=user_data.email,
            failure_reason="inactive_user",
            device_info=device_info,
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Check if user is admin or role-based admin - require OTP for admin logins
    is_admin = user.role.name in ['admin', 'role_admin']
    
    # Determine if OTP is enabled in config
    otp_enabled = getattr(settings, 'email_otp_enabled', False) or getattr(settings, 'sms_otp_enabled', False)
    # Only require OTP for admin if OTP is enabled
    if is_admin and otp_enabled:
        requires_otp = True
    else:
        requires_otp = False
    
    if requires_otp:
        # Log OTP requirement
        login_logger.log_login_attempt(
            email=user.email,
            success=False,
            user=user,
            device_info=device_info,
            ip_address=ip_address,
            otp_required=True,
            admin_login=is_admin
        )
        
        # OTP is enabled, return message to request OTP
        return JSONResponse(
            status_code=200,
            content={
                "message": "OTP verification required",
                "requires_otp": True,
                "email_otp_enabled": getattr(settings, 'email_otp_enabled', False),
                "sms_otp_enabled": getattr(settings, 'sms_otp_enabled', False),
                "admin_login": is_admin
            }
        )
    
    # Normal login flow (no OTP required)
    return perform_login(user, db, login_logger, device_info, ip_address)


def perform_login(user: User, db: Session, login_logger: LoginLogger = None, 
                 device_info: str = None, ip_address: str = None) -> Token:
    """Perform the actual login process"""
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log successful login
    if login_logger:
        login_logger.log_successful_login(
            user=user,
            device_info=device_info,
            ip_address=ip_address,
            admin_login=user.role.name in ['admin', 'role_admin']
        )
    
    # Send login notification
    try:
        from app.services.notification import send_login_notification
        send_login_notification(db, user.id)
    except Exception as e:
        # Log error but don't fail the login
        print(f"Failed to send login notification: {str(e)}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        two_factor_enabled=current_user.two_factor_enabled,
        role=current_user.role.name if current_user.role else None,  # <-- fix here
        default_currency_id=current_user.default_currency_id,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
def update_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        current_user.email = user_update.email
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        two_factor_enabled=current_user.two_factor_enabled,
        role=current_user.role.name,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/change-password")
def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/roles", response_model=List[str])
def get_roles(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get all available roles (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    roles = db.query(Role).all()
    return [role.name for role in roles]


@router.post("/login/verify-otp", response_model=Token)
def verify_login_otp(
    email: str,
    otp_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify OTP for login (especially for admin users)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get device info and IP for logging
    device_info = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    login_logger = LoginLogger(db)
    
    # Verify OTP
    try:
        otp_service = OTPService(db)
        otp_service.verify_otp(
            email=email,
            otp_code=otp_code,
            otp_type="login"
        )
        
        # OTP verified successfully, perform login
        return perform_login(user, db, login_logger, device_info, ip_address)
        
    except Exception as e:
        # Log failed OTP verification
        login_logger.log_failed_login(
            email=email,
            failure_reason="invalid_otp",
            device_info=device_info,
            ip_address=ip_address,
            otp_required=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 