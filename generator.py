#!/usr/bin/env python3
"""
EVM Keypair Generator with Encryption
Generates 10 EVM keypairs and encrypts private keys with a user-provided secret key.
"""

import os
import getpass
from eth_account import Account
from crypto import save_encrypted_file, load_encrypted_file


def generate_evm_keypairs(count=10):
    """Generate EVM keypairs."""
    keypairs = []
    print(f"Generating {count} EVM keypairs...")
    
    for i in range(count):
        # Generate a new account
        account = Account.create()
        keypair = {
            'index': i + 1,
            'private_key': account.key.hex(),
            'public_key': account.address,
        }
        keypairs.append(keypair)
        print(f"Generated keypair {i + 1}: {account.address}")
    
    return keypairs


def generate_evm_keypairs(count=10):
    """Generate EVM keypairs."""
    keypairs = []
    print(f"Generating {count} EVM keypairs...")
    
    for i in range(count):
        # Generate a new account
        account = Account.create()
        keypair = {
            'index': i + 1,
            'private_key': account.key.hex(),
            'public_key': account.address,
        }
        keypairs.append(keypair)
        print(f"Generated keypair {i + 1}: {account.address}")
    
    return keypairs


def export_encrypted_keys(keypairs, secret_key, filename="env.dat"):
    """Export encrypted private keys to a file in KEY_1=... format."""
    print(f"\nEncrypting and exporting private keys to {filename}...")
    
    # Create the content to encrypt (only private keys)
    content_lines = []
    for keypair in keypairs:
        line = f"KEY_{keypair['index']}={keypair['private_key']}"
        content_lines.append(line)
    
    content = "\n".join(content_lines)
    
    # Encrypt and save using crypto module
    save_encrypted_file(content, filename, secret_key)
    
    print(f"✅ Encrypted private keys exported to {filename}")
    print(f"📁 File size: {os.path.getsize(filename)} bytes")


def load_and_decrypt_keys(filename="env.dat", secret_key=None):
    """Load and decrypt private keys from file."""
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return None
    
    if secret_key is None:
        secret_key = getpass.getpass("Enter secret key to decrypt: ")
    
    try:
        # Decrypt using crypto module
        decrypted_content = load_encrypted_file(filename, secret_key)
        print("✅ Successfully decrypted keys (content not displayed for security)")
        return decrypted_content
        
    except Exception as e:
        print(f"❌ Failed to decrypt: {e}")
        return None


def main():
    """Main function."""
    print("🔐 EVM Keypair Generator with Encryption")
    print("=" * 50)
    
    # Generate 10 EVM keypairs
    keypairs = generate_evm_keypairs(10)
    
    print("\n📋 Generated Keypairs Summary:")
    for keypair in keypairs:
        print(f"  {keypair['index']}. Address: {keypair['public_key']}")
    
    # Ask for secret key
    print("\n🔑 Encryption Setup:")
    secret_key = getpass.getpass("Enter a secret key for encryption: ")
    
    if not secret_key:
        print("❌ No secret key provided. Exiting...")
        return
    
    # Confirm secret key
    confirm_key = getpass.getpass("Confirm secret key: ")
    if secret_key != confirm_key:
        print("❌ Secret keys don't match. Exiting...")
        return
    
    # Export encrypted keys
    export_encrypted_keys(keypairs, secret_key)
    
    # Ask if user wants to test decryption
    test_decrypt = input("\n🔍 Test decryption? (y/n): ").lower().strip()
    if test_decrypt == 'y':
        result = load_and_decrypt_keys("env.dat", secret_key)
        if result:
            print("🔒 Decryption test successful (keys validated but not displayed)")
    
    print("\n✨ Process completed successfully!")


if __name__ == "__main__":
    main()
