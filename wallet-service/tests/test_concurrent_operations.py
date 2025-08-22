import pytest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletCreate, WalletOperationRequest, OperationType
from app.core.database import SessionLocal
from app.models.wallet import Wallet


class TestConcurrentOperations:
    """Test cases for concurrent wallet operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create database session."""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture
    def wallet_service(self, db_session):
        """Create wallet service instance."""
        return WalletService(db_session)
    
    @pytest.fixture
    def test_wallet(self, wallet_service):
        """Create a test wallet."""
        wallet_data = WalletCreate(initial_balance=1000.0)
        return wallet_service.create_wallet(wallet_data)
    
    def test_concurrent_deposits(self, wallet_service, test_wallet):
        """Test concurrent deposit operations on the same wallet."""
        wallet_uuid = test_wallet.uuid
        num_threads = 10
        deposit_amount = 100.0
        expected_final_balance = 1000.0 + (num_threads * deposit_amount)
        
        def deposit_operation():
            """Perform a deposit operation."""
            operation_data = WalletOperationRequest(
                operation_type=OperationType.DEPOSIT,
                amount=deposit_amount,
                description="Concurrent deposit test"
            )
            return wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Execute concurrent deposits
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(deposit_operation) for _ in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all operations completed successfully
        assert len(results) == num_threads
        
        # Check final balance
        final_balance = wallet_service.get_wallet_balance(wallet_uuid)
        assert final_balance.balance == expected_final_balance
        
        # Verify all transactions were recorded
        transactions = wallet_service.get_wallet_transactions(wallet_uuid)
        assert len(transactions) == num_threads
        
        # Verify all transactions are deposits
        for transaction in transactions:
            assert transaction.operation_type == "DEPOSIT"
            assert transaction.amount == deposit_amount
    
    def test_concurrent_withdrawals(self, wallet_service, test_wallet):
        """Test concurrent withdrawal operations on the same wallet."""
        wallet_uuid = test_wallet.uuid
        num_threads = 5
        withdrawal_amount = 50.0
        expected_final_balance = 1000.0 - (num_threads * withdrawal_amount)
        
        def withdrawal_operation():
            """Perform a withdrawal operation."""
            operation_data = WalletOperationRequest(
                operation_type=OperationType.WITHDRAW,
                amount=withdrawal_amount,
                description="Concurrent withdrawal test"
            )
            return wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Execute concurrent withdrawals
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(withdrawal_operation) for _ in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all operations completed successfully
        assert len(results) == num_threads
        
        # Check final balance
        final_balance = wallet_service.get_wallet_balance(wallet_uuid)
        assert final_balance.balance == expected_final_balance
        
        # Verify all transactions were recorded
        transactions = wallet_service.get_wallet_transactions(wallet_uuid)
        assert len(transactions) == num_threads
        
        # Verify all transactions are withdrawals
        for transaction in transactions:
            assert transaction.operation_type == "WITHDRAW"
            assert transaction.amount == withdrawal_amount
    
    def test_mixed_concurrent_operations(self, wallet_service, test_wallet):
        """Test mixed concurrent deposit and withdrawal operations."""
        wallet_uuid = test_wallet.uuid
        num_deposits = 8
        num_withdrawals = 3
        deposit_amount = 100.0
        withdrawal_amount = 50.0
        
        expected_final_balance = (
            1000.0 + (num_deposits * deposit_amount) - (num_withdrawals * withdrawal_amount)
        )
        
        def deposit_operation():
            """Perform a deposit operation."""
            operation_data = WalletOperationRequest(
                operation_type=OperationType.DEPOSIT,
                amount=deposit_amount,
                description="Mixed concurrent deposit test"
            )
            return wallet_service.perform_operation(wallet_uuid, operation_data)
        
        def withdrawal_operation():
            """Perform a withdrawal operation."""
            operation_data = WalletOperationRequest(
                operation_type=OperationType.WITHDRAW,
                amount=withdrawal_amount,
                description="Mixed concurrent withdrawal test"
            )
            return wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Execute mixed concurrent operations
        with ThreadPoolExecutor(max_workers=num_deposits + num_withdrawals) as executor:
            deposit_futures = [executor.submit(deposit_operation) for _ in range(num_deposits)]
            withdrawal_futures = [executor.submit(withdrawal_operation) for _ in range(num_withdrawals)]
            
            all_futures = deposit_futures + withdrawal_futures
            results = [future.result() for future in as_completed(all_futures)]
        
        # Verify all operations completed successfully
        assert len(results) == num_deposits + num_withdrawals
        
        # Check final balance
        final_balance = wallet_service.get_wallet_balance(wallet_uuid)
        assert final_balance.balance == expected_final_balance
        
        # Verify all transactions were recorded
        transactions = wallet_service.get_wallet_transactions(wallet_uuid)
        assert len(transactions) == num_deposits + num_withdrawals
        
        # Count deposit and withdrawal transactions
        deposit_count = sum(1 for t in transactions if t.operation_type == "DEPOSIT")
        withdrawal_count = sum(1 for t in transactions if t.operation_type == "WITHDRAW")
        
        assert deposit_count == num_deposits
        assert withdrawal_count == num_withdrawals
    
    def test_concurrent_insufficient_funds(self, wallet_service, test_wallet):
        """Test concurrent withdrawals that would result in insufficient funds."""
        wallet_uuid = test_wallet.uuid
        initial_balance = 100.0
        withdrawal_amount = 50.0
        num_withdrawals = 3  # This will cause insufficient funds for the last withdrawal
        
        # First, set the wallet balance to a known amount
        wallet_service.wallet_repo.update_balance(
            wallet_uuid=wallet_uuid,
            amount=initial_balance - 1000.0,  # Reset to initial_balance
            operation_type="WITHDRAW",
            description="Reset balance for test"
        )
        
        def withdrawal_operation():
            """Perform a withdrawal operation."""
            try:
                operation_data = WalletOperationRequest(
                    operation_type=OperationType.WITHDRAW,
                    amount=withdrawal_amount,
                    description="Concurrent insufficient funds test"
                )
                return wallet_service.perform_operation(wallet_uuid, operation_data)
            except Exception as e:
                return e
        
        # Execute concurrent withdrawals
        with ThreadPoolExecutor(max_workers=num_withdrawals) as executor:
            futures = [executor.submit(withdrawal_operation) for _ in range(num_withdrawals)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify that some operations succeeded and some failed
        successful_operations = [r for r in results if not isinstance(r, Exception)]
        failed_operations = [r for r in results if isinstance(r, Exception)]
        
        # Should have exactly 2 successful withdrawals (100 / 50 = 2)
        assert len(successful_operations) == 2
        assert len(failed_operations) == 1
        
        # Check final balance
        final_balance = wallet_service.get_wallet_balance(wallet_uuid)
        assert final_balance.balance == 0.0  # 100 - (2 * 50) = 0
    
    def test_balance_consistency(self, wallet_service, test_wallet):
        """Test that balance remains consistent under concurrent operations."""
        wallet_uuid = test_wallet.uuid
        num_operations = 20
        operation_amount = 10.0
        
        def mixed_operation(operation_id):
            """Perform a mixed operation based on operation ID."""
            if operation_id % 2 == 0:
                # Even IDs: deposit
                operation_data = WalletOperationRequest(
                    operation_type=OperationType.DEPOSIT,
                    amount=operation_amount,
                    description=f"Deposit operation {operation_id}"
                )
            else:
                # Odd IDs: withdrawal
                operation_data = WalletOperationRequest(
                    operation_type=OperationType.WITHDRAW,
                    amount=operation_amount,
                    description=f"Withdrawal operation {operation_id}"
                )
            return wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Execute mixed concurrent operations
        with ThreadPoolExecutor(max_workers=num_operations) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(num_operations)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all operations completed successfully
        assert len(results) == num_operations
        
        # Calculate expected balance
        deposits = num_operations // 2  # Even numbers
        withdrawals = num_operations // 2  # Odd numbers
        expected_balance = 1000.0 + (deposits * operation_amount) - (withdrawals * operation_amount)
        
        # Check final balance
        final_balance = wallet_service.get_wallet_balance(wallet_uuid)
        assert final_balance.balance == expected_balance
        
        # Verify transaction count
        transactions = wallet_service.get_wallet_transactions(wallet_uuid)
        assert len(transactions) == num_operations + 1  # +1 for initial wallet creation
