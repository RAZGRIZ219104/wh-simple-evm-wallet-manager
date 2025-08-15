#!/usr/bin/env python3
"""
EVM Wallet Manager
Manages multiple EVM wallets, shows balances, and executes transactions.
"""

import os
import re
import getpass
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from crypto import load_encrypted_file
from config import ETHEREUM_RPC, BSC_RPC


# RPC URLs for different networks (using config file)n3
"""
EVM Wallet Manager
Manages multiple EVM wallets, shows balances, and executes transactions.
"""

import os
import re
import getpass
from decimal import Decim    print("=" * 60)
    
    # Initialize Web3 connections
    web3_eth = get_web3_connection('ethereum')
    web3_bsc = get_web3_connection('bsc')om web3 import Web3
from eth_account import Account
from crypto import load_encrypted_file
from config import ETHEREUM_RPC, BSC_RPC


# RPC URLs for different networks (using config file)
RPC_URLS = {
    'ethereum': ETHEREUM_RPC,
    'bsc': BSC_RPC,
}


def get_web3_connection(network):
    """Get a properly configured Web3 connection for the specified network."""
    rpc_url = RPC_URLS.get(network)
    if not rpc_url:
        raise ValueError(f"Unknown network: {network}")
    
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # For BSC (Proof of Authority chain), we handle POA middleware internally
    # Modern web3.py handles this automatically in most cases
    
    return web3

# Token contract addresses
TOKEN_CONTRACTS = {
    'ethereum': {
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    },
    'bsc': {
        'USDT': '0x55d398326f99059fF775485246999027B3197955',
        'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
    }
}

# ERC-20 ABI (minimal for balance and transfer)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]


def load_wallets(filename="env.dat", secret_key=None):
    """Load and decrypt private keys from file."""
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return None
    
    if secret_key is None:
        secret_key = getpass.getpass("Enter secret key to decrypt wallets: ")
    
    try:
        # Decrypt content using crypto module
        decrypted_content = load_encrypted_file(filename, secret_key)
        
        # Parse the KEY_1=... format (ignore ADDR_ lines if present)
        wallets = {}
        for line in decrypted_content.strip().split('\n'):
            if line.startswith('KEY_') and '=' in line:
                key_name, private_key = line.split('=', 1)
                index = int(key_name.replace('KEY_', ''))
                account = Account.from_key(private_key)
                wallets[index] = {
                    'private_key': private_key,
                    'address': account.address,
                    'account': account
                }
        
        print(f"✅ Successfully loaded {len(wallets)} wallets")
        return wallets
        
    except Exception as e:
        print(f"❌ Failed to decrypt wallets: {e}")
        return None


def is_valid_eth_address(address):
    """Validate if address is a valid Ethereum address."""
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def get_balance(web3, address, token_contract=None):
    """Get balance for native token or ERC-20 token."""
    try:
        if token_contract is None:
            # Native token (ETH/BNB)
            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        else:
            # ERC-20 token
            balance_raw = token_contract.functions.balanceOf(address).call()
            decimals = token_contract.functions.decimals().call()
            balance = balance_raw / (10 ** decimals)
            return float(balance)
    except Exception as e:
        print(f"Error getting balance: {e}")
        return 0.0


def show_all_balances(wallets):
    """Show balances for all wallets across different networks."""
    print("\n💰 Wallet Balances Overview")
    print("=" * 80)
    
    # Initialize Web3 connections
    web3_eth = get_web3_connection('ethereum')
    web3_bsc = get_web3_connection('bsc')
    
    # Initialize token contracts
    usdt_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDT'], abi=ERC20_ABI)
    usdc_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDC'], abi=ERC20_ABI)
    usdt_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDT'], abi=ERC20_ABI)
    usdc_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDC'], abi=ERC20_ABI)
    
    for index, wallet in wallets.items():
        address = wallet['address']
        print(f"\n🔑 Wallet {index}: {address}")
        
        # Ethereum balances
        eth_balance = get_balance(web3_eth, address)
        usdt_eth_balance = get_balance(web3_eth, address, usdt_eth)
        usdc_eth_balance = get_balance(web3_eth, address, usdc_eth)
        
        # BSC balances
        bnb_balance = get_balance(web3_bsc, address)
        usdt_bsc_balance = get_balance(web3_bsc, address, usdt_bsc)
        usdc_bsc_balance = get_balance(web3_bsc, address, usdc_bsc)
        
        print(f"  📈 Ethereum: {eth_balance:.6f} ETH")
        print(f"  💵 ERC20-USDT: {usdt_eth_balance:.2f} USDT")
        print(f"  💵 ERC20-USDC: {usdc_eth_balance:.2f} USDC")
        print(f"  📈 BSC: {bnb_balance:.6f} BNB")
        print(f"  💵 BEP20-USDT: {usdt_bsc_balance:.2f} USDT")
        print(f"  💵 BEP20-USDC: {usdc_bsc_balance:.2f} USDC")


def show_wallet_details(wallet, wallet_index):
    """Show detailed balance for a specific wallet."""
    address = wallet['address']
    print(f"\n🔍 Wallet {wallet_index} Details: {address}")
    print("=" * 60)
    
    # Initialize Web3 connections
    web3_eth = Web3(Web3.HTTPProvider(RPC_URLS['ethereum']))
    web3_bsc = Web3(Web3.HTTPProvider(RPC_URLS['bsc']))
    
    # Initialize token contracts
    usdt_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDT'], abi=ERC20_ABI)
    usdc_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDC'], abi=ERC20_ABI)
    usdt_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDT'], abi=ERC20_ABI)
    usdc_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDC'], abi=ERC20_ABI)
    
    # Get balances
    balances = {
        'ETH': get_balance(web3_eth, address),
        'BNB': get_balance(web3_bsc, address),
        'ERC20-USDT': get_balance(web3_eth, address, usdt_eth),
        'ERC20-USDC': get_balance(web3_eth, address, usdc_eth),
        'BEP20-USDT': get_balance(web3_bsc, address, usdt_bsc),
        'BEP20-USDC': get_balance(web3_bsc, address, usdc_bsc),
    }
    
    print("Token Balances:")
    for token, balance in balances.items():
        if 'USDT' in token or 'USDC' in token:
            print(f"  💵 {token}: {balance:.2f}")
        else:
            print(f"  📈 {token}: {balance:.6f}")
    
    return balances


def execute_transaction(wallet, token_type, amount, destination, balances):
    """Execute a transaction."""
    print(f"\n🚀 Preparing Transaction")
    print("=" * 40)
    print(f"From: {wallet['address']}")
    print(f"To: {destination}")
    print(f"Token: {token_type}")
    print(f"Amount: {amount}")
    
    # Check if user has sufficient balance
    if balances[token_type] < float(amount):
        print(f"❌ Insufficient balance. Available: {balances[token_type]:.6f}")
        return
    
    confirm = input("\n⚠️  Confirm transaction? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Transaction cancelled")
        return
    
    try:
        # Initialize Web3 connection based on token type
        if token_type in ['ETH', 'ERC20-USDT', 'ERC20-USDC']:
            web3 = Web3(Web3.HTTPProvider(RPC_URLS['ethereum']))
            network = 'ethereum'
        else:
            web3 = Web3(Web3.HTTPProvider(RPC_URLS['bsc']))
            network = 'bsc'
        
        # Get nonce
        nonce = web3.eth.get_transaction_count(wallet['address'])
        
        # Get gas price
        gas_price = web3.eth.gas_price
        
        if token_type in ['ETH', 'BNB']:
            # Native token transfer
            value = web3.to_wei(amount, 'ether')
            
            transaction = {
                'to': destination,
                'value': value,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
            }
        else:
            # ERC-20/BEP-20 token transfer
            if token_type == 'ERC20-USDT':
                contract_address = TOKEN_CONTRACTS['ethereum']['USDT']
            elif token_type == 'ERC20-USDC':
                contract_address = TOKEN_CONTRACTS['ethereum']['USDC']
            elif token_type == 'BEP20-USDT':
                contract_address = TOKEN_CONTRACTS['bsc']['USDT']
            elif token_type == 'BEP20-USDC':
                contract_address = TOKEN_CONTRACTS['bsc']['USDC']
            
            token_contract = web3.eth.contract(address=contract_address, abi=ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            value = int(float(amount) * (10 ** decimals))
            
            # Build transaction data
            transfer_function = token_contract.functions.transfer(destination, value)
            
            transaction = {
                'to': contract_address,
                'value': 0,
                'gas': 100000,  # Standard gas limit for ERC-20 transfer
                'gasPrice': gas_price,
                'nonce': nonce,
                'data': transfer_function.build_transaction({'gas': 100000})['data']
            }
        
        # Sign transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, wallet['private_key'])
        
        # Send transaction
        print("📡 Broadcasting transaction...")
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        print(f"✅ Transaction sent!")
        print(f"🔗 Transaction hash: {tx_hash.hex()}")
        print(f"🌐 Network: {network.upper()}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt.status == 1:
            print("✅ Transaction confirmed!")
        else:
            print("❌ Transaction failed!")
        
    except Exception as e:
        print(f"❌ Transaction failed: {e}")


def main():
    """Main function."""
    print("💼 EVM Wallet Manager")
    print("=" * 50)
    
    # 1. Ask password and decrypt wallets
    wallets = load_wallets()
    if not wallets:
        return
    
    # 2. Show all balances
    show_all_balances(wallets)
    
    while True:
        print("\n" + "=" * 50)
        print("🎯 What would you like to do?")
        print("1. Show wallet details")
        print("2. Make a transaction")
        print("3. Refresh balances")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # 5. Choose wallet and show balance
            print("\n📋 Available Wallets:")
            for index, wallet in wallets.items():
                print(f"  {index}. {wallet['address']}")
            
            try:
                wallet_choice = int(input("\nEnter wallet number: "))
                if wallet_choice in wallets:
                    show_wallet_details(wallets[wallet_choice], wallet_choice)
                else:
                    print("❌ Invalid wallet number")
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == '2':
            # Transaction flow
            print("\n📋 Available Wallets:")
            for index, wallet in wallets.items():
                print(f"  {index}. {wallet['address']}")
            
            try:
                wallet_choice = int(input("\nEnter wallet number: "))
                if wallet_choice not in wallets:
                    print("❌ Invalid wallet number")
                    continue
                
                selected_wallet = wallets[wallet_choice]
                balances = show_wallet_details(selected_wallet, wallet_choice)
                
                # 6. Input destination wallet
                while True:
                    destination = input("\n🎯 Enter destination address: ").strip()
                    if is_valid_eth_address(destination):
                        break
                    else:
                        print("❌ Invalid EVM address. Please try again.")
                
                # 7. Choose token type
                print("\n💎 Available Token Types:")
                token_types = ['ETH', 'BNB', 'ERC20-USDT', 'ERC20-USDC', 'BEP20-USDT', 'BEP20-USDC']
                for i, token in enumerate(token_types, 1):
                    balance = balances.get(token, 0)
                    if 'USDT' in token or 'USDC' in token:
                        print(f"  {i}. {token} (Balance: {balance:.2f})")
                    else:
                        print(f"  {i}. {token} (Balance: {balance:.6f})")
                
                try:
                    token_choice = int(input("\nEnter token number: "))
                    if 1 <= token_choice <= len(token_types):
                        selected_token = token_types[token_choice - 1]
                    else:
                        print("❌ Invalid token choice")
                        continue
                except ValueError:
                    print("❌ Please enter a valid number")
                    continue
                
                # 8. Input transfer amount
                try:
                    amount = input(f"\n💰 Enter amount to transfer ({selected_token}): ").strip()
                    amount_float = float(amount)
                    if amount_float <= 0:
                        print("❌ Amount must be greater than 0")
                        continue
                except ValueError:
                    print("❌ Please enter a valid amount")
                    continue
                
                # 9. Make transaction
                execute_transaction(selected_wallet, selected_token, amount, destination, balances)
                
            except ValueError:
                print("❌ Please enter a valid number")
        
        elif choice == '3':
            # Refresh balances
            show_all_balances(wallets)
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
