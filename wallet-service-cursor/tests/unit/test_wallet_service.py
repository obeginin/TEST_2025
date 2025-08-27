import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletCreate, WalletOperationRequest, OperationType
from app.core.exceptions import NotFoundError, ValidationError, InsufficientFundsError


class TestWalletService:
    """Test cases for WalletService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def wallet_service(self, mock_db):
        """Create WalletService instance with mock dependencies."""
        with patch('app.services.wallet_service.WalletRepository') as mock_wallet_repo, \
             patch('app.services.wallet_service.TransactionRepository') as mock_transaction_repo:
            
            service = WalletService(mock_db)
            service.wallet_repo = mock_wallet_repo.return_value
            service.transaction_repo = mock_transaction_repo.return_value
            
            yield service
    
    def test_create_wallet_success(self, wallet_service):
        """Test successful wallet creation."""
        # Arrange
        wallet_data = WalletCreate(initial_balance=100.0)
        mock_wallet = Mock(
            uuid="123e4567-e89b-12d3-a456-426614174000",
            balance=Decimal("100.00"),
            currency="USD",
            status="active",
            created_at="2025-01-22T15:20:00",
            updated_at="2025-01-22T15:20:00"
        )
        wallet_service.wallet_repo.create_wallet.return_value = mock_wallet
        
        # Act
        result = wallet_service.create_wallet(wallet_data)
        
        # Assert
        assert result.uuid == "123e4567-e89b-12d3-a456-426614174000"
        assert result.balance == 100.0
        assert result.currency == "USD"
        assert result.status == "active"
        wallet_service.wallet_repo.create_wallet.assert_called_once_with(
            wallet_uuid=None,
            initial_balance=100.0
        )
    
    def test_create_wallet_with_custom_uuid(self, wallet_service):
        """Test wallet creation with custom UUID."""
        # Arrange
        custom_uuid = "custom-uuid-123"
        wallet_data = WalletCreate(uuid=custom_uuid, initial_balance=50.0)
        mock_wallet = Mock(
            uuid=custom_uuid,
            balance=Decimal("50.00"),
            currency="USD",
            status="active",
            created_at="2025-01-22T15:20:00",
            updated_at="2025-01-22T15:20:00"
        )
        wallet_service.wallet_repo.create_wallet.return_value = mock_wallet
        
        # Act
        result = wallet_service.create_wallet(wallet_data)
        
        # Assert
        assert result.uuid == custom_uuid
        wallet_service.wallet_repo.create_wallet.assert_called_once_with(
            wallet_uuid=custom_uuid,
            initial_balance=50.0
        )
    
    def test_create_wallet_validation_error(self, wallet_service):
        """Test wallet creation with validation error."""
        # Arrange
        wallet_data = WalletCreate(initial_balance=100.0)
        wallet_service.wallet_repo.create_wallet.side_effect = ValueError("Wallet already exists")
        
        # Act & Assert
        with pytest.raises(ValidationError):
            wallet_service.create_wallet(wallet_data)
    
    def test_get_wallet_success(self, wallet_service):
        """Test successful wallet retrieval."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_wallet = Mock(
            uuid=wallet_uuid,
            balance=Decimal("150.00"),
            currency="USD",
            status="active",
            created_at="2025-01-22T15:20:00",
            updated_at="2025-01-22T15:20:00"
        )
        wallet_service.wallet_repo.get_by_uuid_or_404.return_value = mock_wallet
        
        # Act
        result = wallet_service.get_wallet(wallet_uuid)
        
        # Assert
        assert result.uuid == wallet_uuid
        assert result.balance == 150.0
        wallet_service.wallet_repo.get_by_uuid_or_404.assert_called_once_with(wallet_uuid)
    
    def test_get_wallet_not_found(self, wallet_service):
        """Test wallet retrieval when wallet doesn't exist."""
        # Arrange
        wallet_uuid = "non-existent-uuid"
        wallet_service.wallet_repo.get_by_uuid_or_404.side_effect = NotFoundError("Wallet", wallet_uuid)
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            wallet_service.get_wallet(wallet_uuid)
    
    def test_get_wallet_balance_success(self, wallet_service):
        """Test successful wallet balance retrieval."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_wallet = Mock(
            uuid=wallet_uuid,
            balance=Decimal("200.00"),
            currency="USD",
            status="active",
            updated_at="2025-01-22T15:20:00"
        )
        wallet_service.wallet_repo.get_by_uuid_or_404.return_value = mock_wallet
        
        # Act
        result = wallet_service.get_wallet_balance(wallet_uuid)
        
        # Assert
        assert result.uuid == wallet_uuid
        assert result.balance == 200.0
        assert result.currency == "USD"
    
    def test_perform_deposit_operation_success(self, wallet_service):
        """Test successful deposit operation."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        operation_data = WalletOperationRequest(
            operation_type=OperationType.DEPOSIT,
            amount=100.0,
            description="Test deposit"
        )
        
        mock_wallet = Mock(uuid=wallet_uuid)
        mock_transaction = Mock(
            id=1,
            balance_before=Decimal("100.00"),
            balance_after=Decimal("200.00"),
            reference_id=None,
            created_at="2025-01-22T15:20:00"
        )
        
        wallet_service.wallet_repo.update_balance.return_value = (mock_wallet, mock_transaction)
        
        # Act
        result = wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Assert
        assert result.wallet_uuid == wallet_uuid
        assert result.operation_type == OperationType.DEPOSIT
        assert result.amount == 100.0
        assert result.balance_before == 100.0
        assert result.balance_after == 200.0
        assert result.transaction_id == 1
        
        wallet_service.wallet_repo.update_balance.assert_called_once_with(
            wallet_uuid=wallet_uuid,
            amount=100.0,
            operation_type="DEPOSIT",
            description="Test deposit",
            reference_id=None
        )
    
    def test_perform_withdraw_operation_success(self, wallet_service):
        """Test successful withdraw operation."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        operation_data = WalletOperationRequest(
            operation_type=OperationType.WITHDRAW,
            amount=50.0,
            description="Test withdrawal"
        )
        
        mock_wallet = Mock(uuid=wallet_uuid)
        mock_transaction = Mock(
            id=2,
            balance_before=Decimal("200.00"),
            balance_after=Decimal("150.00"),
            reference_id="ref123",
            created_at="2025-01-22T15:20:00"
        )
        
        wallet_service.wallet_repo.update_balance.return_value = (mock_wallet, mock_transaction)
        
        # Act
        result = wallet_service.perform_operation(wallet_uuid, operation_data)
        
        # Assert
        assert result.operation_type == OperationType.WITHDRAW
        assert result.amount == 50.0
        assert result.balance_before == 200.0
        assert result.balance_after == 150.0
        assert result.reference_id == "ref123"
    
    def test_perform_withdraw_insufficient_funds(self, wallet_service):
        """Test withdraw operation with insufficient funds."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        operation_data = WalletOperationRequest(
            operation_type=OperationType.WITHDRAW,
            amount=1000.0
        )
        
        wallet_service.wallet_repo.update_balance.side_effect = InsufficientFundsError(
            wallet_uuid, 1000.0, 100.0
        )
        
        # Act & Assert
        with pytest.raises(InsufficientFundsError):
            wallet_service.perform_operation(wallet_uuid, operation_data)
    
    def test_perform_operation_invalid_type(self, wallet_service):
        """Test operation with invalid operation type."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        operation_data = WalletOperationRequest(
            operation_type="INVALID",
            amount=100.0
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            wallet_service.perform_operation(wallet_uuid, operation_data)
    
    def test_validate_wallet_uuid_valid(self, wallet_service):
        """Test UUID validation with valid UUID."""
        # Arrange
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        # Act
        result = wallet_service.validate_wallet_uuid(valid_uuid)
        
        # Assert
        assert result is True
    
    def test_validate_wallet_uuid_invalid(self, wallet_service):
        """Test UUID validation with invalid UUID."""
        # Arrange
        invalid_uuid = "invalid-uuid"
        
        # Act
        result = wallet_service.validate_wallet_uuid(invalid_uuid)
        
        # Assert
        assert result is False
    
    def test_get_wallet_transactions_success(self, wallet_service):
        """Test successful transaction retrieval."""
        # Arrange
        wallet_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_transactions = [
            Mock(
                id=1,
                wallet_id=1,
                operation_type="DEPOSIT",
                amount=Decimal("100.00"),
                balance_before=Decimal("0.00"),
                balance_after=Decimal("100.00"),
                description="Test deposit",
                reference_id=None,
                created_at="2025-01-22T15:20:00"
            )
        ]
        wallet_service.wallet_repo.get_wallet_transactions.return_value = mock_transactions
        
        # Act
        result = wallet_service.get_wallet_transactions(wallet_uuid)
        
        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].operation_type == "DEPOSIT"
        assert result[0].amount == 100.0
        
        wallet_service.wallet_repo.get_wallet_transactions.assert_called_once_with(
            wallet_uuid, 0, 100
        )
