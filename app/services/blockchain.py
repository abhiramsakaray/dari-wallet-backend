from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, List
from decimal import Decimal
import asyncio
import aiohttp
from web3 import Web3
from tronpy import Tron
from solana.rpc.api import Client as SolanaClient
# Bitcoin imports - simplified for now
# from bitcoin import SelectParams
# from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet as XRPLWallet
from app.core.config import settings
from app.core.security import encrypt_private_key, decrypt_private_key
import secrets
import hashlib
import base64


class BlockchainProvider(ABC):
    """Abstract base class for blockchain providers"""
    
    @abstractmethod
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        """Generate wallet and return (address, encrypted_private_key, public_key)"""
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> Decimal:
        """Get native token balance"""
        pass
    
    @abstractmethod
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal, 
                       encrypted_private_key: str, encryption_key: bytes, 
                       gas_price: Optional[Decimal] = None) -> str:
        """Send transaction and return transaction hash"""
        pass
    
    @abstractmethod
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        """Estimate gas for transaction"""
        pass
    
    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """Get transaction status"""
        pass


class EthereumProvider(BlockchainProvider):
    """Ethereum blockchain provider"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.ethereum_rpc_url))
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        account = self.w3.eth.account.create()
        address = account.address
        private_key = account.key.hex()
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return Decimal(str(balance_eth))
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        private_key = decrypt_private_key(encrypted_private_key, encryption_key)
        account = self.w3.eth.account.from_key(private_key)
        
        nonce = self.w3.eth.get_transaction_count(from_address)
        gas_price_wei = gas_price or self.w3.eth.gas_price
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price_wei,
            'chainId': 1
        }
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.w3.to_hex(tx_hash)
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        amount_wei = self.w3.to_wei(amount, 'ether')
        gas_estimate = self.w3.eth.estimate_gas({
            'from': from_address,
            'to': to_address,
            'value': amount_wei
        })
        gas_price = self.w3.eth.gas_price
        return {
            'gas_limit': gas_estimate,
            'gas_price': Decimal(str(self.w3.from_wei(gas_price, 'gwei'))),
            'estimated_fee': Decimal(str(self.w3.from_wei(gas_estimate * gas_price, 'ether')))
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'status': 'confirmed' if receipt and receipt.status == 1 else 'pending',
                'block_number': receipt.blockNumber if receipt else None,
                'gas_used': receipt.gasUsed if receipt else None
            }
        except Exception:
            return {'status': 'failed'}


class BSCProvider(BlockchainProvider):
    """Binance Smart Chain provider"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.bsc_rpc_url))
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        account = self.w3.eth.account.create()
        address = account.address
        private_key = account.key.hex()
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        balance_wei = self.w3.eth.get_balance(address)
        balance_bnb = self.w3.from_wei(balance_wei, 'ether')
        return Decimal(str(balance_bnb))
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        private_key = decrypt_private_key(encrypted_private_key, encryption_key)
        account = self.w3.eth.account.from_key(private_key)
        
        nonce = self.w3.eth.get_transaction_count(from_address)
        gas_price_wei = gas_price or self.w3.eth.gas_price
        amount_wei = self.w3.to_wei(amount, 'ether')
        
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': amount_wei,
            'gas': 21000,
            'gasPrice': gas_price_wei,
            'chainId': 56
        }
        
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.w3.to_hex(tx_hash)
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        amount_wei = self.w3.to_wei(amount, 'ether')
        gas_estimate = self.w3.eth.estimate_gas({
            'from': from_address,
            'to': to_address,
            'value': amount_wei
        })
        gas_price = self.w3.eth.gas_price
        return {
            'gas_limit': gas_estimate,
            'gas_price': Decimal(str(self.w3.from_wei(gas_price, 'gwei'))),
            'estimated_fee': Decimal(str(self.w3.from_wei(gas_estimate * gas_price, 'ether')))
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'status': 'confirmed' if receipt and receipt.status == 1 else 'pending',
                'block_number': receipt.blockNumber if receipt else None,
                'gas_used': receipt.gasUsed if receipt else None
            }
        except Exception:
            return {'status': 'failed'}


class TronProvider(BlockchainProvider):
    """Tron blockchain provider"""
    
    def __init__(self):
        self.client = Tron(network='mainnet')
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        account = self.client.generate_account()
        address = account.address
        private_key = account.private_key.hex()
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        balance_sun = self.client.get_account_balance(address)
        balance_trx = balance_sun / 1_000_000  # Convert from SUN to TRX
        return Decimal(str(balance_trx))
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        private_key = decrypt_private_key(encrypted_private_key, encryption_key)
        account = self.client.get_account(from_address)
        
        amount_sun = int(amount * 1_000_000)  # Convert TRX to SUN
        
        txn = self.client.trx.transfer(
            from_address, to_address, amount_sun
        )
        
        signed_txn = txn.sign(private_key)
        result = signed_txn.broadcast()
        return result['txid']
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        # Tron doesn't use gas in the same way as Ethereum
        return {
            'gas_limit': 0,
            'gas_price': Decimal('0'),
            'estimated_fee': Decimal('0.1')  # Fixed fee for TRX transfers
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        try:
            tx_info = self.client.get_transaction_info(tx_hash)
            return {
                'status': 'confirmed' if tx_info.get('confirmed') else 'pending',
                'block_number': tx_info.get('blockNumber'),
                'gas_used': 0
            }
        except Exception:
            return {'status': 'failed'}


class SolanaProvider(BlockchainProvider):
    """Solana blockchain provider"""
    
    def __init__(self):
        self.client = SolanaClient(settings.solana_rpc_url)
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        # Simplified Solana wallet generation
        private_key_bytes = secrets.token_bytes(32)
        private_key = private_key_bytes.hex()
        # In a real implementation, you'd use proper Solana key derivation
        address = hashlib.sha256(private_key_bytes).hexdigest()[:44]
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        # Simplified balance check
        return Decimal('0')
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        # Simplified Solana transaction
        return f"solana_tx_{secrets.token_hex(16)}"
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        return {
            'gas_limit': 0,
            'gas_price': Decimal('0'),
            'estimated_fee': Decimal('0.000005')  # SOL transaction fee
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        return {'status': 'pending'}


class BitcoinProvider(BlockchainProvider):
    """Bitcoin blockchain provider"""
    
    def __init__(self):
        # Simplified Bitcoin initialization
        pass
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        # Simplified Bitcoin wallet generation
        private_key_bytes = secrets.token_bytes(32)
        private_key = private_key_bytes.hex()
        # In a real implementation, you'd use proper Bitcoin key derivation
        address = hashlib.sha256(private_key_bytes).hexdigest()[:34]
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        # Simplified balance check
        return Decimal('0')
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        # Simplified Bitcoin transaction
        return f"btc_tx_{secrets.token_hex(16)}"
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        return {
            'gas_limit': 0,
            'gas_price': Decimal('0'),
            'estimated_fee': Decimal('0.0001')  # BTC transaction fee
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        return {'status': 'pending'}


class XRPProvider(BlockchainProvider):
    """XRP blockchain provider"""
    
    def __init__(self):
        self.client = JsonRpcClient(settings.xrp_rpc_url)
    
    def generate_wallet(self, encryption_key: bytes) -> Tuple[str, str, str]:
        # Simplified XRP wallet generation
        private_key_bytes = secrets.token_bytes(32)
        private_key = private_key_bytes.hex()
        # In a real implementation, you'd use proper XRP key derivation
        address = hashlib.sha256(private_key_bytes).hexdigest()[:34]
        encrypted_key = encrypt_private_key(private_key, encryption_key)
        return address, encrypted_key, address
    
    def get_balance(self, address: str) -> Decimal:
        # Simplified balance check
        return Decimal('0')
    
    def send_transaction(self, from_address: str, to_address: str, amount: Decimal,
                        encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        # Simplified XRP transaction
        return f"xrp_tx_{secrets.token_hex(16)}"
    
    def estimate_gas(self, from_address: str, to_address: str, amount: Decimal) -> Dict:
        return {
            'gas_limit': 0,
            'gas_price': Decimal('0'),
            'estimated_fee': Decimal('0.00001')  # XRP transaction fee
        }
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        return {'status': 'pending'}


class BlockchainService:
    """Main blockchain service that manages multiple chain providers"""
    
    def __init__(self, chain: str = 'ethereum'):
        # Select provider based on chain
        if chain == 'ethereum':
            self.provider = EthereumProvider()
        elif chain == 'bsc':
            self.provider = BSCProvider()
        elif chain == 'solana':
            self.provider = SolanaProvider()
        elif chain == 'bitcoin':
            self.provider = BitcoinProvider()
        # ... add other chains as needed
        else:
            raise ValueError(f"Unsupported chain: {chain}")

    def generate_wallet(self, encryption_key: bytes):
        return self.provider.generate_wallet(encryption_key)
    
    def get_balance(self, chain: str, address: str) -> Decimal:
        """Get balance for specific chain and address"""
        provider = self.get_provider(chain)
        return provider.get_balance(address)
    
    def send_transaction(self, chain: str, from_address: str, to_address: str, 
                        amount: Decimal, encrypted_private_key: str, encryption_key: bytes,
                        gas_price: Optional[Decimal] = None) -> str:
        """Send transaction on specific chain"""
        provider = self.get_provider(chain)
        return provider.send_transaction(from_address, to_address, amount, 
                                      encrypted_private_key, encryption_key, gas_price)
    
    def estimate_gas(self, chain: str, from_address: str, to_address: str, amount: Decimal) -> Dict:
        """Estimate gas for transaction on specific chain"""
        provider = self.get_provider(chain)
        return provider.estimate_gas(from_address, to_address, amount)
    
    def get_transaction_status(self, chain: str, tx_hash: str) -> Dict:
        """Get transaction status for specific chain"""
        provider = self.get_provider(chain)
        return provider.get_transaction_status(tx_hash)
    
    def get_supported_chains(self) -> List[str]:
        """Get list of supported blockchain chains"""
        return list(self.providers.keys()) 