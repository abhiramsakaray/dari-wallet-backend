from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.wallet import Wallet
from app.models.user import User
from app.models.token_balance import TokenBalance
from app.services.blockchain import BlockchainService
from app.core.security import generate_encryption_key, encrypt_private_key
from app.schemas.wallet import WalletCreate, WalletResponse
import asyncio


class WalletService:
    """Service for wallet management operations"""
    
    def __init__(self):
        self.blockchain_service = BlockchainService()
    
    def create_wallet(self, db: Session, user: User, chain: str) -> Wallet:
        """Create a new wallet for a user on a specific chain"""
        # Generate encryption key for this wallet
        encryption_key = generate_encryption_key()
        # Generate wallet using blockchain service, always pass encryption_key
        blockchain_service = BlockchainService(chain)
        address, encrypted_private_key, public_key = blockchain_service.generate_wallet(encryption_key)
        # Create wallet record
        wallet = Wallet(
       user_id=user.id,
        chain=chain,
        address=address,
        encrypted_private_key=encrypted_private_key,
        public_key=public_key,
        encryption_key=encryption_key.decode()  # Store as string
    )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
        return wallet
    
    def get_user_wallets(self, db: Session, user: User) -> List[Wallet]:
        """Get all wallets for a user"""
        return db.query(Wallet).filter(Wallet.user_id == user.id, Wallet.is_active == True).all()
    
    def get_wallet_by_chain(self, db: Session, user: User, chain: str) -> Optional[Wallet]:
        """Get user's wallet for a specific chain"""
        return db.query(Wallet).filter(
            Wallet.user_id == user.id,
            Wallet.chain == chain,
            Wallet.is_active == True
        ).first()
    
    def delete_wallet(self, db: Session, user: User, chain: str) -> bool:
        """Delete a user's wallet for a specific chain"""
        wallet = self.get_wallet_by_chain(db, user, chain)
        if wallet:
            wallet.is_active = False
            db.commit()
            return True
        return False
    
    def update_wallet_balance(self, db: Session, wallet: Wallet) -> Wallet:
        """Update wallet balance from blockchain"""
        try:
            balance = self.blockchain_service.get_balance(wallet.chain, wallet.address)
            wallet.balance = balance
            db.commit()
            db.refresh(wallet)
        except Exception as e:
            # Log error but don't fail
            print(f"Error updating balance for wallet {wallet.id}: {e}")
        
        return wallet
    
    async def get_wallet_balances(self, db: Session, user: User) -> List[Dict]:
        """Get all wallet balances for a user"""
        from app.services.price import price_service
        wallets = self.get_user_wallets(db, user)
        balances = []
        # Get user's default currency
        user_currency = "usd"  # Default
        if user.default_currency:
            user_currency = user.default_currency.code.lower()
        # CoinGecko coin IDs mapping
        coin_mapping = {
            'ethereum': 'ethereum',
            'bsc': 'binancecoin',
            'tron': 'tron',
            'solana': 'solana',
            'bitcoin': 'bitcoin',
            'xrp': 'ripple',
            'ganache': 'ethereum'  # Use Ethereum price for Ganache testing
        }
        for wallet in wallets:
            try:
                # Update balance from blockchain
                self.update_wallet_balance(db, wallet)
                # Get price in user's default currency
                price_usd = None
                value_in_currency = None
                if wallet.chain in coin_mapping:
                    coin_id = coin_mapping[wallet.chain]
                    price_usd = await price_service.get_crypto_price(coin_id, "usd")
                    if price_usd and wallet.balance:
                        value_in_currency = await price_service.convert_crypto_to_currency(
                            coin_id, wallet.balance, user_currency
                        )
                balance_info = {
                    'chain': wallet.chain,
                    'address': wallet.address,
                    'balance': wallet.balance,
                    'symbol': self._get_native_symbol(wallet.chain),
                    'price_usd': price_usd,
                    'value_in_currency': value_in_currency,
                    'currency': user_currency.upper()
                }
                balances.append(balance_info)
            except Exception as e:
                print(f"Error getting balance for wallet {wallet.id}: {e}")
                # Add wallet with basic info even if price fetch fails
                balance_info = {
                    'chain': wallet.chain,
                    'address': wallet.address,
                    'balance': wallet.balance,
                    'symbol': self._get_native_symbol(wallet.chain),
                    'price_usd': None,
                    'value_in_currency': None,
                    'currency': user_currency.upper()
                }
                balances.append(balance_info)
        return balances
    
    def export_wallets(self, db: Session, user: User) -> List[Dict]:
        """Export user's wallet addresses"""
        wallets = self.get_user_wallets(db, user)
        export_data = []
        
        for wallet in wallets:
            export_data.append({
                'chain': wallet.chain,
                'address': wallet.address,
                'public_key': wallet.public_key,
                'created_at': wallet.created_at
            })
        
        return export_data
    
    def _get_native_symbol(self, chain: str) -> str:
        """Get native token symbol for a chain"""
        symbols = {
            'ethereum': 'ETH',
            'bsc': 'BNB',
            'tron': 'TRX',
            'solana': 'SOL',
            'bitcoin': 'BTC',
            'xrp': 'XRP'
        }
        return symbols.get(chain, chain.upper())
    
    def get_token_balances(self, db: Session, user: User, chain: str) -> List[Dict]:
        """Get token balances for a user's wallet on a specific chain"""
        wallet = self.get_wallet_by_chain(db, user, chain)
        if not wallet:
            return []
        
        token_balances = db.query(TokenBalance).filter(
            TokenBalance.wallet_id == wallet.id
        ).all()
        
        balances = []
        for tb in token_balances:
            balance_info = {
                'symbol': tb.token.symbol,
                'name': tb.token.name,
                'balance': tb.balance,
                'decimals': tb.token.decimals,
                'price_usd': tb.token.price_usd,
                'value_usd': None,  # Would be calculated
                'contract_address': tb.token.contract_address,
                'logo_url': tb.token.logo_url
            }
            balances.append(balance_info)
        
        return balances