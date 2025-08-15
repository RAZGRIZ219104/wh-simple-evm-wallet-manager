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


def load_wallets():
    """Load and decrypt wallets from env.dat file."""
    if not os.path.exists("env.dat"):
        print("❌ env.dat file not found!")
        print("   Please run generator.py first to create encrypted wallets.")
        return None
    
    secret_key = getpass.getpass("🔐 Enter decryption password: ")
    
    try:
        # Decrypt content using crypto module
        decrypted_content = load_encrypted_file("env.dat", secret_key)
        
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
            return balance
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
        
        # Get native token balances
        eth_balance = get_balance(web3_eth, address)
        bnb_balance = get_balance(web3_bsc, address)
        
        # Get ERC-20/BEP-20 token balances
        usdt_eth_balance = get_balance(web3_eth, address, usdt_eth)
        usdc_eth_balance = get_balance(web3_eth, address, usdc_eth)
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
    web3_eth = get_web3_connection('ethereum')
    web3_bsc = get_web3_connection('bsc')
    
    # Initialize token contracts
    usdt_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDT'], abi=ERC20_ABI)
    usdc_eth = web3_eth.eth.contract(address=TOKEN_CONTRACTS['ethereum']['USDC'], abi=ERC20_ABI)
    usdt_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDT'], abi=ERC20_ABI)
    usdc_bsc = web3_bsc.eth.contract(address=TOKEN_CONTRACTS['bsc']['USDC'], abi=ERC20_ABI)
    
    # Get balances
    balances = {
        'ETH': get_balance(web3_eth, address),
        'BNB': get_balance(web3_bsc, address),
        'USDT-ETH': get_balance(web3_eth, address, usdt_eth),
        'USDC-ETH': get_balance(web3_eth, address, usdc_eth),
        'USDT-BSC': get_balance(web3_bsc, address, usdt_bsc),
        'USDC-BSC': get_balance(web3_bsc, address, usdc_bsc),
    }
    
    print("💰 Balances:")
    print(f"  ETH: {balances['ETH']:.6f}")
    print(f"  BNB: {balances['BNB']:.6f}")
    print(f"  USDT (Ethereum): {balances['USDT-ETH']:.2f}")
    print(f"  USDC (Ethereum): {balances['USDC-ETH']:.2f}")
    print(f"  USDT (BSC): {balances['USDT-BSC']:.2f}")
    print(f"  USDC (BSC): {balances['USDC-BSC']:.2f}")


def execute_transaction(wallet, network, token_type, recipient, amount):
    """Execute a transaction from the specified wallet."""
    print(f"\n🚀 Executing Transaction")
    print("=" * 40)
    
    try:
        if network.lower() == 'ethereum':
            web3 = get_web3_connection('ethereum')
        elif network.lower() == 'bsc':
            web3 = get_web3_connection('bsc')
        else:
            print("❌ Invalid network. Use 'ethereum' or 'bsc'")
            return False
        
        from_address = wallet['address']
        account = wallet['account']
        
        print(f"From: {from_address}")
        print(f"To: {recipient}")
        print(f"Amount: {amount} {token_type}")
        print(f"Network: {network}")
        
        # Get current gas price
        gas_price = web3.eth.gas_price
        
        if token_type.upper() in ['ETH', 'BNB']:
            # Native token transfer
            amount_wei = web3.to_wei(amount, 'ether')
            
            transaction = {
                'to': recipient,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': web3.eth.get_transaction_count(from_address),
                'chainId': web3.eth.chain_id
            }
            
        else:
            # ERC-20/BEP-20 token transfer
            token_address = TOKEN_CONTRACTS[network.lower()].get(token_type.upper())
            if not token_address:
                print(f"❌ Token {token_type} not supported on {network}")
                return False
            
            token_contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            
            transaction = {
                'to': token_address,
                'value': 0,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': web3.eth.get_transaction_count(from_address),
                'data': token_contract.functions.transfer(recipient, amount_wei).build_transaction({
                    'gas': 100000,
                    'gasPrice': gas_price,
                })['data'],
                'chainId': web3.eth.chain_id
            }
        
        # Sign and send transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, wallet['private_key'])
        
        print("\n⚠️  TRANSACTION READY TO SEND")
        print(f"Estimated gas fee: {web3.from_wei(gas_price * transaction['gas'], 'ether'):.8f} {token_type if token_type.upper() in ['ETH', 'BNB'] else 'ETH' if network.lower() == 'ethereum' else 'BNB'}")
        
        confirm = input("\n🔥 Send this transaction? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("❌ Transaction cancelled")
            return False
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"✅ Transaction sent! Hash: {tx_hash.hex()}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt.status == 1:
            print(f"✅ Transaction confirmed! Block: {receipt.blockNumber}")
            return True
        else:
            print("❌ Transaction failed!")
            return False
            
    except Exception as e:
        print(f"❌ Transaction error: {e}")
        return False


def main():
    """Main function to run the wallet manager."""
    print("💼 EVM Wallet Manager")
    print("=" * 50)
    
    # Load wallets
    wallets = load_wallets()
    if not wallets:
        return
    
    while True:
        print("\n📋 Options:")
        print("1. Show all wallet balances")
        print("2. Show specific wallet details")
        print("3. Send transaction")
        print("4. Exit")
        
        try:
            choice = input("\n👉 Choose option (1-4): ").strip()
            
            if choice == '1':
                show_all_balances(wallets)
                
            elif choice == '2':
                print("\nAvailable wallets:")
                for index in sorted(wallets.keys()):
                    print(f"  {index}: {wallets[index]['address']}")
                
                try:
                    wallet_index = int(input("\n👉 Enter wallet number: "))
                    if wallet_index in wallets:
                        show_wallet_details(wallets[wallet_index], wallet_index)
                    else:
                        print("❌ Invalid wallet number")
                except ValueError:
                    print("❌ Please enter a valid number")
                    
            elif choice == '3':
                print("\nAvailable wallets:")
                for index in sorted(wallets.keys()):
                    print(f"  {index}: {wallets[index]['address']}")
                
                try:
                    wallet_index = int(input("\n👉 Enter wallet number: "))
                    if wallet_index not in wallets:
                        print("❌ Invalid wallet number")
                        continue
                    
                    wallet = wallets[wallet_index]
                    
                    print("\nNetworks: ethereum, bsc")
                    network = input("👉 Enter network: ").strip()
                    
                    print("\nTokens: ETH, BNB, USDT, USDC")
                    token_type = input("👉 Enter token type: ").strip()
                    
                    recipient = input("👉 Enter recipient address: ").strip()
                    if not is_valid_eth_address(recipient):
                        print("❌ Invalid recipient address")
                        continue
                    
                    amount = float(input("👉 Enter amount: ").strip())
                    if amount <= 0:
                        print("❌ Amount must be greater than 0")
                        continue
                    
                    execute_transaction(wallet, network, token_type, recipient, amount)
                    
                except ValueError:
                    print("❌ Please enter valid values")
                    
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
