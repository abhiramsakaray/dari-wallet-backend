from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.alias import Alias, WalletAlias
from app.models.wallet import Wallet
from app.schemas.alias import AliasCreate, AliasResponse, AliasResolveResponse, WalletAliasResponse, AliasUpdate

router = APIRouter(prefix="/alias", tags=["Username Resolution"])


@router.post("/set", response_model=AliasResponse)
def set_alias(
    alias_data: AliasCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set or update username alias"""
    # Check if username is already taken
    existing_alias = db.query(Alias).filter(Alias.username == alias_data.username).first()
    if existing_alias and existing_alias.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Get or create alias
    if existing_alias and existing_alias.user_id == current_user.id:
        alias = existing_alias
    else:
        alias = Alias(
            username=alias_data.username,
            user_id=current_user.id
        )
        db.add(alias)
        db.commit()
        db.refresh(alias)
    
    return AliasResponse(
        id=alias.id,
        username=alias.username,
        is_active=alias.is_active,
        is_verified=alias.is_verified,
        created_at=alias.created_at
    )


@router.get("/resolve/{username}", response_model=AliasResolveResponse)
def resolve_alias(
    username: str,
    db: Session = Depends(get_db)
):
    """Resolve username to wallet addresses"""
    alias = db.query(Alias).filter(
        Alias.username == username,
        Alias.is_active == True
    ).first()
    
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username not found"
        )
    
    # Get wallet aliases for this username
    wallet_aliases = db.query(WalletAlias).filter(
        WalletAlias.alias_id == alias.id
    ).all()
    
    wallets = []
    for wa in wallet_aliases:
        wallet = db.query(Wallet).filter(Wallet.id == wa.wallet_id).first()
        if wallet:
            wallets.append(WalletAliasResponse(
                chain=wa.chain,
                address=wallet.address,
                is_primary=wa.is_primary
            ))
    
    return AliasResolveResponse(
        username=alias.username,
        wallets=wallets,
        is_verified=alias.is_verified
    )


@router.get("/my-alias", response_model=AliasResponse)
def get_my_alias(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's alias"""
    alias = db.query(Alias).filter(
        Alias.user_id == current_user.id,
        Alias.is_active == True
    ).first()
    
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alias found for user"
        )
    
    return AliasResponse(
        id=alias.id,
        username=alias.username,
        is_active=alias.is_active,
        is_verified=alias.is_verified,
        created_at=alias.created_at
    )


@router.put("/update", response_model=AliasResponse)
def update_alias(
    alias_update: AliasUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update alias settings"""
    alias = db.query(Alias).filter(
        Alias.user_id == current_user.id,
        Alias.is_active == True
    ).first()
    
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alias found for user"
        )
    
    if alias_update.is_active is not None:
        alias.is_active = alias_update.is_active
    if alias_update.is_verified is not None:
        alias.is_verified = alias_update.is_verified
    
    db.commit()
    db.refresh(alias)
    
    return AliasResponse(
        id=alias.id,
        username=alias.username,
        is_active=alias.is_active,
        is_verified=alias.is_verified,
        created_at=alias.created_at
    )


@router.post("/link-wallet/{chain}")
def link_wallet_to_alias(
    chain: str,
    is_primary: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Link a wallet to user's alias"""
    # Get user's alias
    alias = db.query(Alias).filter(
        Alias.user_id == current_user.id,
        Alias.is_active == True
    ).first()
    
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alias found for user"
        )
    
    # Get user's wallet for this chain
    wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.chain == chain,
        Wallet.is_active == True
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet found for chain {chain}"
        )
    
    # Check if wallet is already linked
    existing_link = db.query(WalletAlias).filter(
        WalletAlias.alias_id == alias.id,
        WalletAlias.wallet_id == wallet.id
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet for {chain} is already linked to alias"
        )
    
    # If this is primary, unset other primary wallets for this chain
    if is_primary:
        db.query(WalletAlias).filter(
            WalletAlias.alias_id == alias.id,
            WalletAlias.chain == chain
        ).update({"is_primary": False})
    
    # Create wallet alias link
    wallet_alias = WalletAlias(
        alias_id=alias.id,
        wallet_id=wallet.id,
        chain=chain,
        is_primary=is_primary
    )
    
    db.add(wallet_alias)
    db.commit()
    
    return {"message": f"Wallet for {chain} linked to alias successfully"}


@router.delete("/unlink-wallet/{chain}")
def unlink_wallet_from_alias(
    chain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlink a wallet from user's alias"""
    # Get user's alias
    alias = db.query(Alias).filter(
        Alias.user_id == current_user.id,
        Alias.is_active == True
    ).first()
    
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alias found for user"
        )
    
    # Get wallet alias link
    wallet_alias = db.query(WalletAlias).filter(
        WalletAlias.alias_id == alias.id,
        WalletAlias.chain == chain
    ).first()
    
    if not wallet_alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet linked for chain {chain}"
        )
    
    db.delete(wallet_alias)
    db.commit()
    
    return {"message": f"Wallet for {chain} unlinked from alias successfully"} 