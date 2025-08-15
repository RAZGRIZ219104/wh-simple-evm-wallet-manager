#!/usr/bin/env python3
"""
Decrypt EVM Private Keys
Utility script to decrypt the encrypted private keys file.
"""

import os
import getpass
from eth_account import Account
from crypto import load_encrypted_file, save_decrypted_file


def main():
    """Main function to decrypt keys."""
    print("🔓 EVM Private Keys Decryptor")
    print("=" * 40)
    
    filename = input("Enter filename (default: env.dat): ").strip()
    if not filename:
        filename = "env.dat"
    
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return
    
    secret_key = getpass.getpass("Enter secret key to decrypt: ")
    
    try:
        # Decrypt content using crypto module
        decrypted_content = load_encrypted_file(filename, secret_key)
        
        print("\n✅ Successfully decrypted keys")
        print("🔒 For security, keys are not displayed in terminal")
        
        # Parse the decrypted content and derive public addresses
        enhanced_content_lines = []
        for line in decrypted_content.strip().split('\n'):
            if line.startswith('KEY_') and '=' in line:
                # Add the private key line
                enhanced_content_lines.append(line)
                
                # Derive and add the public address
                key_name, private_key = line.split('=', 1)
                index = key_name.replace('KEY_', '')
                
                try:
                    # Derive public address from private key
                    account = Account.from_key(private_key)
                    address_line = f"ADDR_{index}={account.address}"
                    enhanced_content_lines.append(address_line)
                except Exception as e:
                    print(f"⚠️  Warning: Could not derive address for KEY_{index}: {e}")
        
        enhanced_content = "\n".join(enhanced_content_lines)
        
        # Always save to env.dec.dat as the decrypted output with addresses
        output_file = "env.dec.dat"
        save_decrypted_file(enhanced_content, output_file)
        
        print(f"✅ Decrypted keys with addresses saved to {output_file}")
        print("⚠️  Remember to delete this file after use for security!")
        
        # Ask if user wants to save to a custom file as well
        save_custom = input("\n💾 Save to additional custom file? (y/n): ").lower().strip()
        if save_custom == 'y':
            custom_file = input("Enter custom filename: ").strip()
            if custom_file:
                save_decrypted_file(enhanced_content, custom_file)
                print(f"✅ Decrypted keys with addresses also saved to {custom_file}")
        
    except Exception as e:
        print(f"❌ Failed to decrypt: {e}")


if __name__ == "__main__":
    main()
