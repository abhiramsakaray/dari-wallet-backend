from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.token import Token
from app.models.log import Log
from app.models.role import Role
from app.schemas.admin import (
    AdminStats, UserAdminResponse, RoleUpdate, TokenAdd, 
    SystemLog, BroadcastMessage, RPCConfig
)
from app.services.pin import PINService
from app.services.login_logger import LoginLogger
from decimal import Decimal

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserAdminResponse])
def get_all_users(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(offset).limit(limit).all()
    
    user_responses = []
    for user in users:
        # Count user's wallets and transactions
        wallet_count = db.query(Wallet).filter(Wallet.user_id == user.id).count()
        transaction_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
        
        user_responses.append(UserAdminResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role.name,
            created_at=user.created_at,
            last_login=user.last_login,
            wallet_count=wallet_count,
            transaction_count=transaction_count
        ))
    
    return user_responses


@router.get("/user/{user_id}", response_model=UserAdminResponse)
def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    wallet_count = db.query(Wallet).filter(Wallet.user_id == user.id).count()
    transaction_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
    
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role.name,
        created_at=user.created_at,
        last_login=user.last_login,
        wallet_count=wallet_count,
        transaction_count=transaction_count
    )


@router.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Deactivate user instead of deleting
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}


@router.put("/user/{user_id}/role")
def change_user_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Change user role (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.name == role_update.role).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    user.role_id = role.id
    db.commit()
    
    return {"message": f"User role changed to {role_update.role}"}


@router.post("/user/{user_id}/unblock")
def unblock_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Unblock a user from PIN restrictions (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unblock yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    pin_service = PINService(db)
    pin_service.unblock_user(user)
    
    return {"message": "User unblocked successfully"}


@router.get("/login-statistics")
def get_login_statistics(
    user_id: Optional[int] = None,
    days: int = 30,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get login statistics for fraud analysis (admin only)"""
    login_logger = LoginLogger(db)
    stats = login_logger.get_login_statistics(user_id, days)
    return stats


@router.get("/suspicious-activity")
def get_suspicious_activity(
    user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get suspicious login activity (admin only)"""
    login_logger = LoginLogger(db)
    activity = login_logger.get_suspicious_activity(user_id)
    return activity


@router.get("/login-logs")
def get_login_logs(
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get login logs for analysis (admin only)"""
    from app.models.login_log import LoginLog
    
    query = db.query(LoginLog)
    if user_id:
        query = query.filter(LoginLog.user_id == user_id)
    
    logs = query.order_by(LoginLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "email": log.email,
                "success": log.success,
                "device_info": log.device_info,
                "ip_address": log.ip_address,
                "location": log.location,
                "failure_reason": log.failure_reason,
                "otp_required": log.otp_required,
                "otp_verified": log.otp_verified,
                "admin_login": log.admin_login,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": query.count()
    }


@router.get("/wallets/all")
def get_all_wallets(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all wallet records (admin only)"""
    wallets = db.query(Wallet).offset(offset).limit(limit).all()
    
    wallet_data = []
    for wallet in wallets:
        user = db.query(User).filter(User.id == wallet.user_id).first()
        wallet_data.append({
            "id": wallet.id,
            "chain": wallet.chain,
            "address": wallet.address,
            "balance": wallet.balance,
            "is_active": wallet.is_active,
            "user_email": user.email if user else None,
            "user_username": user.username if user else None,
            "created_at": wallet.created_at
        })
    
    return {"wallets": wallet_data}


@router.post("/token/add/{chain}")
def add_token(
    chain: str,
    token_data: TokenAdd,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add support for a new token (admin only)"""
    # Check if token already exists
    existing_token = db.query(Token).filter(
        Token.chain == chain,
        Token.symbol == token_data.symbol
    ).first()
    
    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token {token_data.symbol} already exists on {chain}"
        )
    
    token = Token(
        chain=chain,
        symbol=token_data.symbol,
        name=token_data.name,
        contract_address=token_data.contract_address,
        decimals=token_data.decimals,
        logo_url=token_data.logo_url,
        website=token_data.website,
        description=token_data.description
    )
    
    db.add(token)
    db.commit()
    db.refresh(token)
    
    return {"message": f"Token {token_data.symbol} added successfully"}


@router.get("/token/list/{chain}")
def list_tokens(
    chain: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List tokens for a specific chain (admin only)"""
    tokens = db.query(Token).filter(
        Token.chain == chain,
        Token.is_active == True
    ).all()
    
    token_data = []
    for token in tokens:
        token_data.append({
            "id": token.id,
            "symbol": token.symbol,
            "name": token.name,
            "contract_address": token.contract_address,
            "decimals": token.decimals,
            "is_native": token.is_native,
            "price_usd": token.price_usd,
            "is_active": token.is_active,
            "created_at": token.created_at
        })
    
    return {"tokens": token_data}


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_transactions = db.query(Transaction).count()
    total_wallets = db.query(Wallet).filter(Wallet.is_active == True).count()
    
    # Calculate total volume (simplified)
    transactions = db.query(Transaction).filter(Transaction.status == "confirmed").all()
    total_volume = sum(tx.amount for tx in transactions if tx.amount)
    
    # Get supported chains
    chains = db.query(Wallet.chain).distinct().all()
    chains_supported = [chain[0] for chain in chains]
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_transactions=total_transactions,
        total_volume_usd=Decimal(str(total_volume)),
        total_wallets=total_wallets,
        chains_supported=chains_supported
    )


@router.post("/broadcast")
def broadcast_message(
    message: BroadcastMessage,
    current_user: User = Depends(require_admin)
):
    """Broadcast message to all users (admin only)"""
    # This would typically send notifications to all users
    # For now, just return success
    return {
        "message": "Broadcast sent successfully",
        "title": message.title,
        "content": message.message,
        "type": message.type
    }


@router.post("/rpc/set/{chain}")
def set_rpc_config(
    chain: str,
    rpc_config: RPCConfig,
    current_user: User = Depends(require_admin)
):
    """Set or change RPC URL for a chain (admin only)"""
    # This would update the RPC configuration
    # For now, just return success
    return {
        "message": f"RPC configuration updated for {chain}",
        "chain": chain,
        "rpc_url": rpc_config.rpc_url
    }


@router.get("/logs", response_model=List[SystemLog])
def get_system_logs(
    level: str = None,
    category: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system logs (admin only)"""
    query = db.query(Log)
    
    if level:
        query = query.filter(Log.level == level)
    if category:
        query = query.filter(Log.category == category)
    
    logs = query.order_by(Log.created_at.desc()).offset(offset).limit(limit).all()
    
    log_responses = []
    for log in logs:
        log_responses.append(SystemLog(
            id=log.id,
            level=log.level,
            category=log.category,
            message=log.message,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
            user_id=log.user_id
        ))
    
    return log_responses


@router.get("/logs/{log_type}")
def get_filtered_logs(
    log_type: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get filtered logs by type (admin only)"""
    valid_types = ["errors", "transfers", "auth", "admin", "system"]
    if log_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid log type. Valid types: {valid_types}"
        )
    
    query = db.query(Log)
    
    if log_type == "errors":
        query = query.filter(Log.level == "ERROR")
    elif log_type == "transfers":
        query = query.filter(Log.category == "transaction")
    elif log_type == "auth":
        query = query.filter(Log.category == "auth")
    elif log_type == "admin":
        query = query.filter(Log.category == "admin")
    elif log_type == "system":
        query = query.filter(Log.category == "system")
    
    logs = query.order_by(Log.created_at.desc()).offset(offset).limit(limit).all()
    
    log_data = []
    for log in logs:
        log_data.append({
            "id": log.id,
            "level": log.level,
            "category": log.category,
            "message": log.message,
            "details": log.details,
            "created_at": log.created_at,
            "user_id": log.user_id
        })
    
    return {"logs": log_data} 