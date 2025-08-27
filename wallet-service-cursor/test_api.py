#!/usr/bin/env python3
"""
Simple test script for the Wallet Service API.
Run this after starting the application with docker-compose.
"""

import requests
import json
import uuid
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/wallets"


def test_health_check():
    """Test health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_create_wallet() -> str:
    """Test wallet creation and return wallet UUID."""
    print("💰 Testing wallet creation...")
    
    wallet_data = {
        "initial_balance": 1000.0,
        "currency": "USD"
    }
    
    response = requests.post(API_BASE, json=wallet_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        wallet_uuid = result["data"]["uuid"]
        print(f"✅ Wallet created successfully: {wallet_uuid}")
        print(f"Balance: ${result['data']['balance']}")
        print()
        return wallet_uuid
    else:
        print(f"❌ Failed to create wallet: {response.text}")
        print()
        return None


def test_get_wallet_balance(wallet_uuid: str):
    """Test getting wallet balance."""
    print(f"💳 Testing get wallet balance for {wallet_uuid}...")
    
    response = requests.get(f"{API_BASE}/{wallet_uuid}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Wallet balance: ${result['data']['balance']}")
        print()
    else:
        print(f"❌ Failed to get wallet: {response.text}")
        print()


def test_deposit_operation(wallet_uuid: str, amount: float):
    """Test deposit operation."""
    print(f"💸 Testing deposit operation: ${amount}...")
    
    operation_data = {
        "operation_type": "DEPOSIT",
        "amount": amount,
        "description": "Test deposit"
    }
    
    response = requests.post(f"{API_BASE}/{wallet_uuid}/operation", json=operation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Deposit successful!")
        print(f"Balance before: ${result['data']['balance_before']}")
        print(f"Balance after: ${result['data']['balance_after']}")
        print()
    else:
        print(f"❌ Deposit failed: {response.text}")
        print()


def test_withdraw_operation(wallet_uuid: str, amount: float):
    """Test withdraw operation."""
    print(f"💸 Testing withdraw operation: ${amount}...")
    
    operation_data = {
        "operation_type": "WITHDRAW",
        "amount": amount,
        "description": "Test withdrawal"
    }
    
    response = requests.post(f"{API_BASE}/{wallet_uuid}/operation", json=operation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Withdrawal successful!")
        print(f"Balance before: ${result['data']['balance_before']}")
        print(f"Balance after: ${result['data']['balance_after']}")
        print()
    else:
        print(f"❌ Withdrawal failed: {response.text}")
        print()


def test_insufficient_funds(wallet_uuid: str):
    """Test withdrawal with insufficient funds."""
    print(f"💸 Testing insufficient funds scenario...")
    
    operation_data = {
        "operation_type": "WITHDRAW",
        "amount": 10000.0,  # Much more than available
        "description": "Test insufficient funds"
    }
    
    response = requests.post(f"{API_BASE}/{wallet_uuid}/operation", json=operation_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        result = response.json()
        print(f"✅ Insufficient funds handled correctly!")
        print(f"Error: {result['message']}")
        print()
    else:
        print(f"❌ Unexpected response: {response.text}")
        print()


def test_get_transactions(wallet_uuid: str):
    """Test getting wallet transactions."""
    print(f"📋 Testing get transactions for {wallet_uuid}...")
    
    response = requests.get(f"{API_BASE}/{wallet_uuid}/transactions")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        transactions = result["data"]
        print(f"✅ Found {len(transactions)} transactions:")
        for tx in transactions:
            print(f"  - {tx['operation_type']}: ${tx['amount']} (Balance: ${tx['balance_before']} → ${tx['balance_after']})")
        print()
    else:
        print(f"❌ Failed to get transactions: {response.text}")
        print()


def test_invalid_uuid():
    """Test with invalid UUID."""
    print("🚫 Testing invalid UUID...")
    
    invalid_uuid = "invalid-uuid-format"
    response = requests.get(f"{API_BASE}/{invalid_uuid}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Invalid UUID handled correctly!")
        print()
    else:
        print(f"❌ Unexpected response: {response.text}")
        print()


def test_nonexistent_wallet():
    """Test with non-existent wallet UUID."""
    print("🚫 Testing non-existent wallet...")
    
    fake_uuid = str(uuid.uuid4())
    response = requests.get(f"{API_BASE}/{fake_uuid}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Non-existent wallet handled correctly!")
        print()
    else:
        print(f"❌ Unexpected response: {response.text}")
        print()


def main():
    """Run all tests."""
    print("🚀 Starting Wallet Service API Tests")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test wallet creation
    wallet_uuid = test_create_wallet()
    if not wallet_uuid:
        print("❌ Cannot continue without a wallet. Exiting.")
        return
    
    # Test get wallet balance
    test_get_wallet_balance(wallet_uuid)
    
    # Test deposit operations
    test_deposit_operation(wallet_uuid, 500.0)
    test_deposit_operation(wallet_uuid, 250.0)
    
    # Test withdraw operations
    test_withdraw_operation(wallet_uuid, 100.0)
    test_withdraw_operation(wallet_uuid, 75.0)
    
    # Test insufficient funds
    test_insufficient_funds(wallet_uuid)
    
    # Test get transactions
    test_get_transactions(wallet_uuid)
    
    # Test error cases
    test_invalid_uuid()
    test_nonexistent_wallet()
    
    print("✅ All tests completed!")


if __name__ == "__main__":
    main()
