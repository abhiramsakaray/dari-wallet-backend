from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.otp import OTPType, OTPChannel
from app.services.otp import OTPService
from app.schemas.otp import (
    OTPRequest, OTPVerify, OTPResponse, OTPVerifyResponse,
    OTPConfigCreate, OTPConfigUpdate, OTPConfigResponse, OTPConfigList
)

router = APIRouter(prefix="/otp", tags=["OTP Management"])


@router.post("/request", response_model=OTPResponse)
def request_otp(
    otp_request: OTPRequest,
    db: Session = Depends(get_db)
):
    """Request OTP for login or other purposes"""
    try:
        service = OTPService(db)
        result = service.request_otp(
            email=otp_request.email,
            otp_type=otp_request.otp_type,
            channel=otp_request.channel
        )
        return OTPResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request OTP"
        )


@router.post("/verify", response_model=OTPVerifyResponse)
def verify_otp(
    otp_verify: OTPVerify,
    db: Session = Depends(get_db)
):
    """Verify OTP and get access tokens"""
    try:
        service = OTPService(db)
        result = service.verify_otp(
            email=otp_verify.email,
            otp_code=otp_verify.otp_code,
            otp_type=otp_verify.otp_type
        )
        return OTPVerifyResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )


@router.get("/status")
def get_otp_status(
    otp_type: OTPType = OTPType.LOGIN,
    channel: OTPChannel = OTPChannel.EMAIL,
    db: Session = Depends(get_db)
):
    """Check if OTP is enabled for specific type and channel"""
    service = OTPService(db)
    is_enabled = service.is_otp_enabled(otp_type, channel)
    
    return {
        "otp_type": otp_type.value,
        "channel": channel.value,
        "is_enabled": is_enabled
    }


# Admin routes for OTP configuration
@router.get("/admin/configs", response_model=OTPConfigList)
def get_otp_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all OTP configurations (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = OTPService(db)
    configs = db.query(service.db.query(OTPConfig).offset(skip).limit(limit).all())
    
    return OTPConfigList(
        configs=configs,
        total=len(configs)
    )


@router.post("/admin/configs", response_model=OTPConfigResponse)
def create_otp_config(
    config_data: OTPConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new OTP configuration (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if config already exists
    existing_config = db.query(OTPConfig).filter(
        OTPConfig.name == config_data.name
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP configuration with this name already exists"
        )
    
    config = OTPConfig(**config_data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.put("/admin/configs/{config_id}", response_model=OTPConfigResponse)
def update_otp_config(
    config_id: int,
    config_data: OTPConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update OTP configuration (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    config = db.query(OTPConfig).filter(OTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP configuration not found"
        )
    
    for key, value in config_data.dict(exclude_unset=True).items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/admin/configs/{config_id}")
def delete_otp_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete OTP configuration (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    config = db.query(OTPConfig).filter(OTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP configuration not found"
        )
    
    db.delete(config)
    db.commit()
    
    return {"message": "OTP configuration deleted successfully"}


@router.post("/admin/cleanup")
def cleanup_expired_otps(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clean up expired OTPs (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = OTPService(db)
    cleaned_count = service.cleanup_expired_otps()
    
    return {
        "message": f"Cleaned up {cleaned_count} expired OTPs",
        "cleaned_count": cleaned_count
    }


@router.get("/admin/stats")
def get_otp_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get OTP statistics (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from app.models.otp import OTP, OTPStatus
    
    # Get OTP statistics
    total_otps = db.query(OTP).count()
    pending_otps = db.query(OTP).filter(OTP.status == OTPStatus.PENDING).count()
    verified_otps = db.query(OTP).filter(OTP.status == OTPStatus.VERIFIED).count()
    expired_otps = db.query(OTP).filter(OTP.status == OTPStatus.EXPIRED).count()
    failed_otps = db.query(OTP).filter(OTP.status == OTPStatus.FAILED).count()
    
    # Get enabled configs
    enabled_configs = db.query(OTPConfig).filter(OTPConfig.is_enabled == True).count()
    total_configs = db.query(OTPConfig).count()
    
    return {
        "otp_statistics": {
            "total": total_otps,
            "pending": pending_otps,
            "verified": verified_otps,
            "expired": expired_otps,
            "failed": failed_otps
        },
        "config_statistics": {
            "enabled": enabled_configs,
            "total": total_configs,
            "disabled": total_configs - enabled_configs
        }
    } 