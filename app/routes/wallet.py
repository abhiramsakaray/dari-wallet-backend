from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.token import Token
from app.services.wallet import WalletService
from app.services.transaction import TransactionService
from app.schemas.wallet import (
    WalletCreate, WalletResponse, TransactionCreate, TransactionResponse,
    TokenTransfer, TokenBalance, GasEstimate, QRCodeResponse, QRCodeScan
)
from app.schemas.pin import PINVerifyRequest
from app.services.pin import PINService
from app.services.analytics import AnalyticsService
from app.services.transaction_history import TransactionHistoryService
import qrcode
import base64
import io

router = APIRouter(prefix="/wallet", tags=["Wallet Management"])
wallet_service = WalletService()
transaction_service = TransactionService()


@router.post("/create", response_model=WalletResponse)
def create_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new wallet for a specific chain"""
    # Check if wallet already exists for this chain
    existing_wallet = wallet_service.get_wallet_by_chain(db, current_user, wallet_data.chain)
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet already exists for {wallet_data.chain}"
        )
    
    wallet = wallet_service.create_wallet(db, current_user, wallet_data.chain)
    
    return WalletResponse(
        id=wallet.id,
        chain=wallet.chain,
        address=wallet.address,
        balance=wallet.balance,
        is_active=wallet.is_active,
        created_at=wallet.created_at,
        last_sync=wallet.last_sync
    )


@router.post("/create/{chain}", response_model=WalletResponse)
def create_wallet_for_chain(
    chain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a wallet for a specific chain"""
    wallet_data = WalletCreate(chain=chain)
    return create_wallet(wallet_data, current_user, db)


@router.get("/wallets", response_model=List[WalletResponse])
def get_wallets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all user wallets"""
    wallets = wallet_service.get_user_wallets(db, current_user)
    
    wallet_responses = []
    for wallet in wallets:
        # Update balance from blockchain
        wallet_service.update_wallet_balance(db, wallet)
        
        wallet_responses.append(WalletResponse(
            id=wallet.id,
            chain=wallet.chain,
            address=wallet.address,
            balance=wallet.balance,
            is_active=wallet.is_active,
            created_at=wallet.created_at,
            last_sync=wallet.last_sync
        ))
    
    return wallet_responses


@router.get("/{chain}", response_model=WalletResponse)
def get_wallet(
    chain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's wallet for a specific chain"""
    wallet = wallet_service.get_wallet_by_chain(db, current_user, chain)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet found for chain {chain}"
        )
    
    # Update balance from blockchain
    wallet_service.update_wallet_balance(db, wallet)
    
    return WalletResponse(
        id=wallet.id,
        chain=wallet.chain,
        address=wallet.address,
        balance=wallet.balance,
        is_active=wallet.is_active,
        created_at=wallet.created_at,
        last_sync=wallet.last_sync
    )


@router.get("/wallets/export")
def export_wallets(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export user's wallet addresses"""
    export_data = wallet_service.export_wallets(db, current_user)
    return {"wallets": export_data}


@router.delete("/delete/{chain}")
def delete_wallet(
    chain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a user's wallet for a specific chain"""
    success = wallet_service.delete_wallet(db, current_user, chain)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet found for chain {chain}"
        )
    
    return {"message": f"Wallet for {chain} deleted successfully"}


@router.get("/analytics/frequent-transfers")
def get_frequent_transfers(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's most frequently transferred addresses"""
    analytics_service = AnalyticsService(db)
    frequent_transfers = analytics_service.get_frequent_transfers(current_user.id, limit)
    return {"frequent_transfers": frequent_transfers}


@router.get("/analytics/peak-usage")
def get_peak_usage_times(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's peak usage times"""
    analytics_service = AnalyticsService(db)
    peak_usage = analytics_service.get_peak_usage_times(current_user.id, days)
    return peak_usage


@router.get("/analytics/patterns")
def get_transaction_patterns(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction patterns for fraud analysis"""
    analytics_service = AnalyticsService(db)
    patterns = analytics_service.get_transaction_patterns(current_user.id)
    return patterns


@router.get("/analytics/fraud-indicators")
def get_fraud_indicators(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get fraud indicators based on transaction history"""
    analytics_service = AnalyticsService(db)
    indicators = analytics_service.get_fraud_indicators(current_user.id)
    return indicators


@router.get("/transaction/history/comprehensive")
def get_comprehensive_transaction_history(
    chain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive transaction history with fraud analysis data"""
    history_service = TransactionHistoryService(db)
    history = history_service.get_comprehensive_transaction_history(
        current_user.id, chain, limit, offset
    )
    return {"transactions": history}


@router.get("/transaction/patterns")
def get_transaction_patterns(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction patterns for fraud analysis"""
    history_service = TransactionHistoryService(db)
    patterns = history_service.get_transaction_patterns(current_user.id, days)
    return patterns


@router.get("/transaction/frequent-recipients")
def get_frequent_recipients(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get most frequently transferred addresses"""
    history_service = TransactionHistoryService(db)
    recipients = history_service.get_frequent_recipients(current_user.id, limit)
    return {"frequent_recipients": recipients}


@router.post("/transaction/send", response_model=TransactionResponse)
def send_transaction(
    transaction_data: TransactionCreate,
    pin_verify: PINVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a transaction with PIN verification"""
    # Verify PIN before proceeding with transaction
    pin_service = PINService(db)
    pin_service.verify_pin(current_user, pin_verify.pin)
    
    # Get device info, IP, and location for fraud analysis
    device_info = request.headers.get("user-agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    location = "Unknown"  # In production, you might use a geolocation service
    
    try:
        transaction = transaction_service.send_transaction(
            db, current_user, transaction_data, 
            device_info=device_info, 
            ip_address=ip_address, 
            location=location
        )
        
        # Send transfer notification
        try:
            from app.services.notification import send_transfer_notification
            currency = transaction.token.symbol if transaction.token else "NATIVE"
            send_transfer_notification(
                db, 
                current_user.id, 
                str(transaction.amount), 
                currency, 
                "sent"
            )
        except Exception as e:
            # Log error but don't fail the transaction
            print(f"Failed to send transfer notification: {str(e)}")
        
        return TransactionResponse(
            id=transaction.id,
            tx_hash=transaction.tx_hash,
            chain=transaction.chain,
            from_address=transaction.from_address,
            to_address=transaction.to_address,
            amount=transaction.amount,
            gas_price=transaction.gas_price,
            gas_used=transaction.gas_used,
            gas_limit=transaction.gas_limit,
            fee=transaction.fee,
            block_number=transaction.block_number,
            status=transaction.status,
            is_incoming=transaction.is_incoming,
            memo=transaction.memo,
            token_symbol=transaction.token.symbol if transaction.token else None,
            created_at=transaction.created_at,
            confirmed_at=transaction.confirmed_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/transaction/history", response_model=List[TransactionResponse])
def get_transaction_history(
    chain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction history"""
    history = transaction_service.get_transaction_history(db, current_user, chain, limit, offset)
    return history


@router.get("/transaction/history/{chain}", response_model=List[TransactionResponse])
def get_transaction_history_for_chain(
    chain: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction history for a specific chain"""
    history = transaction_service.get_transaction_history(db, current_user, chain, limit, offset)
    return history


@router.post("/token/transfer", response_model=TransactionResponse)
def transfer_token(
    token_data: TokenTransfer,
    pin_verify: PINVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Transfer tokens with PIN verification"""
    transaction_data = TransactionCreate(
        chain=token_data.chain,
        to_address=token_data.to_address,
        amount=token_data.amount,
        token_symbol=token_data.token_symbol,
        gas_price=token_data.gas_price,
        gas_limit=token_data.gas_limit
    )
    
    # Call the send_transaction function directly
    return send_transaction(transaction_data, pin_verify, request, current_user, db)


@router.get("/tokens/{chain}", response_model=List[TokenBalance])
def get_supported_tokens(
    chain: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get supported tokens for a chain"""
    tokens = db.query(Token).filter(
        Token.chain == chain,
        Token.is_active == True
    ).all()
    
    token_balances = []
    for token in tokens:
        token_balances.append(TokenBalance(
            symbol=token.symbol,
            name=token.name,
            balance=0,  # Would be fetched from user's wallet
            decimals=token.decimals,
            price_usd=token.price_usd,
            value_usd=None,
            contract_address=token.contract_address,
            logo_url=token.logo_url
        ))
    
    return token_balances


@router.get("/{chain}/token/{symbol}/balance", response_model=TokenBalance)
def get_token_balance(
    chain: str,
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get token balance for a specific token"""
    token = db.query(Token).filter(
        Token.chain == chain,
        Token.symbol == symbol,
        Token.is_active == True
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Token {symbol} not found on {chain}"
        )
    
    # Get user's wallet for this chain
    wallet = wallet_service.get_wallet_by_chain(db, current_user, chain)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet found for chain {chain}"
        )
    
    # Get token balance
    from app.models.token_balance import TokenBalance as TokenBalanceModel
    token_balance = db.query(TokenBalanceModel).filter(
        TokenBalanceModel.wallet_id == wallet.id,
        TokenBalanceModel.token_id == token.id
    ).first()
    
    balance = token_balance.balance if token_balance else 0
    
    return TokenBalance(
        symbol=token.symbol,
        name=token.name,
        balance=balance,
        decimals=token.decimals,
        price_usd=token.price_usd,
        value_usd=None,
        contract_address=token.contract_address,
        logo_url=token.logo_url
    )


@router.get("/{chain}/token/{symbol}/txs", response_model=List[TransactionResponse])
def get_token_transactions(
    chain: str,
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction history for a specific token"""
    transactions = transaction_service.get_token_transactions(db, current_user, chain, symbol)
    return transactions


@router.get("/{chain}/qr", response_model=QRCodeResponse)
def generate_qr_code(
    chain: str,
    amount: Optional[float] = None,
    memo: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate QR code for receiving funds"""
    wallet = wallet_service.get_wallet_by_chain(db, current_user, chain)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No wallet found for chain {chain}"
        )
    
    # Create QR code data
    qr_data = {
        "address": wallet.address,
        "chain": chain
    }
    if amount:
        qr_data["amount"] = amount
    if memo:
        qr_data["memo"] = memo
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return QRCodeResponse(
        qr_code=qr_base64,
        address=wallet.address,
        amount=amount,
        memo=memo
    )


@router.post("/scan-qr")
def scan_qr_code(
    qr_data: QRCodeScan,
    current_user: User = Depends(get_current_active_user)
):
    """Scan QR code and decode address & amount"""
    # This would decode the QR code data
    # For now, return the raw data
    return {"decoded_data": qr_data.qr_data}


@router.get("/balances", response_model=List[dict])
def get_wallet_balances(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all wallet balances"""
    balances = wallet_service.get_wallet_balances(db, current_user)
    return balances


@router.get("/{chain}/txs", response_model=List[TransactionResponse])
def get_chain_transactions(
    chain: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction history for a specific chain"""
    history = transaction_service.get_transaction_history(db, current_user, chain, limit, offset)
    return history 