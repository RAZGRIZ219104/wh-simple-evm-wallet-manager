# EVM Wallet Manager

This project provides a complete EVM wallet management solution with keypair generation, encryption, and transaction capabilities.

## Features

- ✅ Generate 10 EVM keypairs (private key + public address)
- 🔐 Encrypt private keys using Fernet symmetric encryption (AES 128 in CBC mode)
- 🔑 Password-based key derivation (PBKDF2 with SHA256)
- 📁 Export encrypted keys in KEY_1=... format
- 💰 View balances across Ethereum and BSC networks
- 💎 Support for ETH, BNB, USDT, and USDC tokens
- 🚀 Execute transactions directly from the interface
- 🔓 Decrypt keys utility script

## Files

- `main.py` - Wallet manager with balance checking and transaction functionality
- `generator.py` - Script to generate and encrypt keypairs
- `decrypt.py` - Utility script to decrypt the encrypted keys (creates `env.dec.dat`)
- `crypto.py` - Cryptographic functions for encryption/decryption
- `config.py` - Configuration file for RPC URLs
- `env.dat` - Encrypted private keys only
- `env.dec.dat` - Decrypted private keys + public addresses (created by decrypt.py)
- `.gitignore` - Git ignore file (excludes sensitive files)

## Usage

### Generate Keypairs (First Time Setup)

```bash
python generator.py
```

The script will:

1. Generate 10 EVM keypairs
2. Display the public addresses
3. Ask for a secret key (password) for encryption
4. Encrypt all private keys and save to `env.dat`
5. Optionally test decryption (keys are validated but not displayed for security)

### Manage Wallets and Make Transactions

```bash
python main.py
```

The wallet manager will:

1. Ask for your secret key to decrypt wallets
2. Load all wallets and show balance overview
3. Allow you to:
   - View detailed wallet balances
   - Make transactions between wallets
   - Refresh balance information
   - Exit the application

### Transaction Features

- ✅ **Multi-Network Support**: Ethereum and BSC networks
- 💎 **Token Support**: ETH, BNB, ERC20-USDT, ERC20-USDC, BEP20-USDT, BEP20-USDC
- 🔍 **Balance Checking**: Real-time balance queries across all networks
- 🎯 **Address Validation**: Ensures destination addresses are valid EVM addresses
- 🚀 **Transaction Execution**: Sign and broadcast transactions
- ⏳ **Confirmation Waiting**: Wait for transaction confirmations

### Decrypt Keys

```bash
python decrypt.py
```

This utility will:

1. Ask for the encrypted file name (default: `env.dat`)
2. Prompt for the secret key
3. Decrypt keys (not displayed in terminal for security)
4. Derive public addresses from private keys
5. Automatically save both private keys and addresses to `env.dec.dat`
6. Optionally save to an additional custom file

## Security Features

- **PBKDF2**: Uses 100,000 iterations for key derivation
- **Salt**: Random 16-byte salt for each encryption
- **Fernet**: Industry-standard symmetric encryption
- **No Plain Text Storage**: Private keys are never stored in plain text
- **No Terminal Logging**: Decrypted keys are never displayed in terminal for security

## Output Format

**Encrypted file (`env.dat`)** contains only private keys:

```
KEY_1=703c26a4cedc2cf37912a3df5b3474fc91bc9398acf8b1777c4b54d5451c0639
KEY_2=ad2f121d7c33ad55462b8b81aff40e9a6c92f59b406a602c43f863baf6b51ea0
KEY_3=79a60cc86c846d27ac4287e6294f6b6655219c5f536494146ba81a9aabe7d8d0
...
```

**Decrypted file (`env.dec.dat`)** contains private keys + derived public addresses:

```
KEY_1=703c26a4cedc2cf37912a3df5b3474fc91bc9398acf8b1777c4b54d5451c0639
ADDR_1=0x577BCc41ad8F0cD4a18F07a402965d0C1Cb6C1cA
KEY_2=ad2f121d7c33ad55462b8b81aff40e9a6c92f59b406a602c43f863baf6b51ea0
ADDR_2=0xbe906a262B7FD5C57285C729A779Fc12b57e924a
KEY_3=79a60cc86c846d27ac4287e6294f6b6655219c5f536494146ba81a9aabe7d8d0
ADDR_3=0x3A0A2BEc0997F1C4a7Fbcb75d3b8BEA81cc69Dd9
...
```

## Dependencies

- `eth-account` - For EVM keypair generation
- `cryptography` - For encryption/decryption
- `web3` - For blockchain interactions
- `requests` - For HTTP requests
- `getpass` - For secure password input

## Installation

```bash
# Install required packages
pip install eth-account cryptography web3 requests

# Generate your keypairs first
python generator.py

# Then use the wallet manager
python main.py
```

## Configuration

Before using the wallet manager, consider updating `config.py` with your own RPC URLs:

1. **Get Alchemy API Key**: Sign up at [Alchemy](https://www.alchemy.com/) for better Ethereum RPC performance
2. **Update config.py**: Replace the demo URLs with your API keys
3. **Alternative RPCs**: You can also use Infura, Ankr, or other RPC providers

## Security Notes

⚠️ **Important Security Considerations:**

1. **Keep your secret key safe** - Without it, you cannot decrypt your private keys
2. **Never share your private keys** - They control access to your wallets
3. **Use a strong secret key** - Consider using a passphrase generator
4. **Backup your encrypted file** - Store `env.dat` securely
5. **Delete decrypted files** - Don't leave private keys in plain text files
6. **Private keys never shown in terminal** - For maximum security, decrypted keys are only saved to files when requested

## Example Session

```
🔐 EVM Keypair Generator with Encryption
==================================================
Generating 10 EVM keypairs...
Generated keypair 1: 0x577BCc41ad8F0cD4a18F07a402965d0C1Cb6C1cA
Generated keypair 2: 0xbe906a262B7FD5C57285C729A779Fc12b57e924a
...

📋 Generated Keypairs Summary:
  1. Address: 0x577BCc41ad8F0cD4a18F07a402965d0C1Cb6C1cA
  2. Address: 0xbe906a262B7FD5C57285C729A779Fc12b57e924a
  ...

🔑 Encryption Setup:
Enter a secret key for encryption: [hidden]
Confirm secret key: [hidden]

✅ Encrypted private keys exported to env.dat
📁 File size: 1052 bytes

🔍 Test decryption? (y/n): y
✅ Successfully decrypted keys (content not displayed for security)
🔒 Decryption test successful (keys validated but not displayed)

✨ Process completed successfully!
```
