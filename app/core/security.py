from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import secrets
import string
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for private keys
def generate_encryption_key():
    """Generate a new encryption key for private key storage"""
    return Fernet.generate_key()

def get_fernet_cipher(key: bytes):
    """Get Fernet cipher for encryption/decryption"""
    return Fernet(key)

def encrypt_private_key(private_key: str, encryption_key: bytes) -> str:
    """Encrypt private key for secure storage"""
    cipher = get_fernet_cipher(encryption_key)
    return cipher.encrypt(private_key.encode()).decode()

def decrypt_private_key(encrypted_key: str, encryption_key: bytes) -> str:
    """Decrypt private key for usage"""
    cipher = get_fernet_cipher(encryption_key)
    return cipher.decrypt(encrypted_key.encode()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    # Always encode sub as string for compatibility
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token, with error logging"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        print("JWT decode error:", e)
        return None

def generate_secure_password(length: int = 32) -> str:
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_mnemonic_phrase() -> str:
    """Generate a mnemonic phrase for wallet creation"""
    # This would typically use a library like bip39
    # For now, returning a placeholder
    return " ".join([secrets.token_hex(4) for _ in range(12)]) 