"""Encryption utilities for API keys"""
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_fernet() -> Fernet:
    """Get Fernet cipher instance"""
    # Ensure key is properly formatted (32 bytes, base64 encoded)
    key = settings.encryption_key.encode()
    if len(key) != 32:
        # Derive a proper key from the provided encryption key
        key = hashlib.sha256(key).digest()
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    fernet = get_fernet()
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    fernet = get_fernet()
    decrypted = fernet.decrypt(encrypted_key.encode())
    return decrypted.decode()
