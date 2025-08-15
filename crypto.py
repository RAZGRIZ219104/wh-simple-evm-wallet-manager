#!/usr/bin/env python3
"""
Cryptographic functions for EVM wallet encryption/decryption.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Derive a Fernet-compatible key from a password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return key, salt


def encrypt_data(data: str, password: str) -> tuple:
    """Encrypt data using Fernet symmetric encryption."""
    key, salt = derive_key_from_password(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode('utf-8'))
    return encrypted_data, salt


def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> str:
    """Decrypt data using Fernet symmetric encryption."""
    key, _ = derive_key_from_password(password, salt)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')


def load_encrypted_file(filename: str, password: str) -> str:
    """Load and decrypt an encrypted file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found!")
    
    with open(filename, 'rb') as f:
        # Read salt (first 16 bytes)
        salt = f.read(16)
        # Read encrypted content
        encrypted_content = f.read()
    
    # Decrypt content
    decrypted_content = decrypt_data(encrypted_content, password, salt)
    return decrypted_content


def save_encrypted_file(data: str, filename: str, password: str) -> None:
    """Encrypt data and save to file."""
    encrypted_content, salt = encrypt_data(data, password)
    
    with open(filename, 'wb') as f:
        # Write salt first (16 bytes)
        f.write(salt)
        # Write encrypted content
        f.write(encrypted_content)


def save_decrypted_file(data: str, filename: str) -> None:
    """Save decrypted data to a plain text file."""
    with open(filename, 'w') as f:
        f.write(data)
