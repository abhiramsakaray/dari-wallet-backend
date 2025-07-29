from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.token import Token
from app.models.user import User
from app.services.blockchain import BlockchainService
from app.core.security import decrypt_private_key
from app.schemas.wallet import TransactionCreate, TransactionResponse
import asyncio


class TransactionService:
    """Service for transaction operations"""
    
    def __init__(self):
        self.blockchain_service = BlockchainService()
    
    def send_transaction(self, db: Session, user: User, transaction_data: TransactionCreate, 
                        device_info: str = None, ip_address: str = None, location: str = None) -> Transaction:
        """Send a transaction on the blockchain"""
        # Get user's wallet for the chain
        wallet = db.query(Wallet).filter(
            Wallet.user_id == user.id,
            Wallet.chain == transaction_data.chain,
            Wallet.is_active == True
        ).first()
        
        if not wallet:
            raise ValueError(f"No wallet found for chain {transaction_data.chain}")
        
        # Check if it's a token transfer
        token = None
        if transaction_data.token_symbol:
            token = db.query(Token).filter(
                Token.chain == transaction_data.chain,
                Token.symbol == transaction_data.token_symbol,
                Token.is_active == True
            ).first()
            
            if not token:
                raise ValueError(f"Token {transaction_data.token_symbol} not supported on {transaction_data.chain}")
        
        # Decrypt private key
        encryption_key = wallet.encryption_key.encode()
        private_key = decrypt_private_key(wallet.encrypted_private_key, encryption_key)
        
        # Send transaction on blockchain
        tx_hash = self.blockchain_service.send_transaction(
            chain=transaction_data.chain,
            from_address=wallet.address,
            to_address=transaction_data.to_address,
            amount=transaction_data.amount,
            encrypted_private_key=wallet.encrypted_private_key,
            encryption_key=encryption_key,
            gas_price=transaction_data.gas_price
        )
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            wallet_id=wallet.id,
            token_id=token.id if token else None,
            tx_hash=tx_hash,
            chain=transaction_data.chain,
            from_address=wallet.address,
            to_address=transaction_data.to_address,
            amount=transaction_data.amount,
            gas_price=transaction_data.gas_price,
            gas_limit=transaction_data.gas_limit,
            status="pending",
            is_incoming=False,
            memo=transaction_data.memo,
            device_info=device_info,
            ip_address=ip_address,
            location=location
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    def get_user_transactions(self, db: Session, user: User, chain: Optional[str] = None) -> List[Transaction]:
        """Get all transactions for a user"""
        query = db.query(Transaction).filter(Transaction.user_id == user.id)
        
        if chain:
            query = query.filter(Transaction.chain == chain)
        
        return query.order_by(Transaction.created_at.desc()).all()
    
    def get_transaction_by_hash(self, db: Session, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        return db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
    
    def update_transaction_status(self, db: Session, transaction: Transaction) -> Transaction:
        """Update transaction status from blockchain"""
        try:
            status_info = self.blockchain_service.get_transaction_status(transaction.chain, transaction.tx_hash)
            
            transaction.status = status_info['status']
            if status_info.get('block_number'):
                transaction.block_number = status_info['block_number']
            if status_info.get('gas_used'):
                transaction.gas_used = status_info['gas_used']
            
            if status_info['status'] == 'confirmed':
                transaction.confirmed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(transaction)
            
        except Exception as e:
            print(f"Error updating transaction status for {transaction.tx_hash}: {e}")
        
        return transaction
    
    def get_transaction_history(self, db: Session, user: User, chain: Optional[str] = None, 
                              limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get transaction history for a user"""
        transactions = self.get_user_transactions(db, user, chain)
        transactions = transactions[offset:offset + limit]
        
        history = []
        for tx in transactions:
            # Update status from blockchain
            self.update_transaction_status(db, tx)
            
            tx_data = {
                'id': tx.id,
                'tx_hash': tx.tx_hash,
                'chain': tx.chain,
                'from_address': tx.from_address,
                'to_address': tx.to_address,
                'amount': tx.amount,
                'gas_price': tx.gas_price,
                'gas_used': tx.gas_used,
                'gas_limit': tx.gas_limit,
                'fee': tx.fee,
                'block_number': tx.block_number,
                'status': tx.status,
                'is_incoming': tx.is_incoming,
                'memo': tx.memo,
                'token_symbol': tx.token.symbol if tx.token else None,
                'created_at': tx.created_at,
                'confirmed_at': tx.confirmed_at
            }
            history.append(tx_data)
        
        return history
    
    def estimate_gas(self, db: Session, user: User, transaction_data: TransactionCreate) -> Dict:
        """Estimate gas for a transaction"""
        wallet = db.query(Wallet).filter(
            Wallet.user_id == user.id,
            Wallet.chain == transaction_data.chain,
            Wallet.is_active == True
        ).first()
        
        if not wallet:
            raise ValueError(f"No wallet found for chain {transaction_data.chain}")
        
        gas_estimate = self.blockchain_service.estimate_gas(
            chain=transaction_data.chain,
            from_address=wallet.address,
            to_address=transaction_data.to_address,
            amount=transaction_data.amount
        )
        
        return gas_estimate
    
    def get_token_transactions(self, db: Session, user: User, chain: str, token_symbol: str) -> List[Dict]:
        """Get token transaction history for a user"""
        token = db.query(Token).filter(
            Token.chain == chain,
            Token.symbol == token_symbol,
            Token.is_active == True
        ).first()
        
        if not token:
            return []
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.chain == chain,
            Transaction.token_id == token.id
        ).order_by(Transaction.created_at.desc()).all()
        
        token_txs = []
        for tx in transactions:
            self.update_transaction_status(db, tx)
            
            tx_data = {
                'id': tx.id,
                'tx_hash': tx.tx_hash,
                'from_address': tx.from_address,
                'to_address': tx.to_address,
                'amount': tx.amount,
                'status': tx.status,
                'is_incoming': tx.is_incoming,
                'created_at': tx.created_at,
                'confirmed_at': tx.confirmed_at
            }
            token_txs.append(tx_data)
        
        return token_txs 