from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from ..repositories.wallet_repo import WalletRepository, TransactionRepository
from ..schemas.wallet import (
    WalletCreate, WalletResponse, WalletOperationRequest, WalletOperationResponse,
    TransactionResponse, WalletBalanceResponse
)
from ..core.exceptions import NotFoundError, ValidationError, InsufficientFundsError
from ..models.wallet import Wallet, Transaction
import logging
import uuid

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.wallet_repo = WalletRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    def create_wallet(self, wallet_data: WalletCreate) -> WalletResponse:
        """Create a new wallet."""
        try:
            # Validate UUID format if provided
            if wallet_data.uuid and not self.validate_wallet_uuid(wallet_data.uuid):
                raise ValidationError(f"Invalid UUID format: {wallet_data.uuid}")
            
            wallet = self.wallet_repo.create_wallet(
                wallet_uuid=wallet_data.uuid,
                initial_balance=wallet_data.initial_balance
            )
            
            return WalletResponse(
                uuid=wallet.uuid,
                balance=float(wallet.balance),
                currency=wallet.currency,
                status=wallet.status,
                created_at=wallet.created_at,
                updated_at=wallet.updated_at
            )
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            raise
    
    def get_wallet(self, wallet_uuid: str) -> WalletResponse:
        """Get wallet by UUID."""
        try:
            wallet = self.wallet_repo.get_by_uuid_or_404(wallet_uuid)
            
            return WalletResponse(
                uuid=wallet.uuid,
                balance=float(wallet.balance),
                currency=wallet.currency,
                status=wallet.status,
                created_at=wallet.created_at,
                updated_at=wallet.updated_at
            )
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet {wallet_uuid}: {e}")
            raise
    
    def get_wallet_balance(self, wallet_uuid: str) -> WalletBalanceResponse:
        """Get wallet balance."""
        try:
            wallet = self.wallet_repo.get_by_uuid_or_404(wallet_uuid)
            
            return WalletBalanceResponse(
                uuid=wallet.uuid,
                balance=float(wallet.balance),
                currency=wallet.currency,
                status=wallet.status,
                last_updated=wallet.updated_at
            )
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet balance {wallet_uuid}: {e}")
            raise
    
    def perform_operation(
        self, 
        wallet_uuid: str, 
        operation_data: WalletOperationRequest
    ) -> WalletOperationResponse:
        """Perform wallet operation (deposit or withdraw)."""
        try:
            # Validate operation type
            if operation_data.operation_type not in ["DEPOSIT", "WITHDRAW"]:
                raise ValidationError(f"Invalid operation type: {operation_data.operation_type}")
            
            # Perform the operation with transaction logging
            wallet, transaction = self.wallet_repo.update_balance(
                wallet_uuid=wallet_uuid,
                amount=operation_data.amount,
                operation_type=operation_data.operation_type,
                description=operation_data.description,
                reference_id=operation_data.reference_id
            )
            
            return WalletOperationResponse(
                wallet_uuid=wallet.uuid,
                operation_type=operation_data.operation_type,
                amount=operation_data.amount,
                balance_before=float(transaction.balance_before),
                balance_after=float(transaction.balance_after),
                transaction_id=transaction.id,
                reference_id=transaction.reference_id,
                created_at=transaction.created_at
            )
            
        except (NotFoundError, InsufficientFundsError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error performing operation on wallet {wallet_uuid}: {e}")
            raise
    
    def get_wallet_transactions(
        self, 
        wallet_uuid: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TransactionResponse]:
        """Get transactions for a specific wallet."""
        try:
            transactions = self.wallet_repo.get_wallet_transactions(
                wallet_uuid=wallet_uuid,
                skip=skip,
                limit=limit
            )
            
            return [
                TransactionResponse(
                    id=transaction.id,
                    wallet_id=transaction.wallet_id,
                    operation_type=transaction.operation_type,
                    amount=float(transaction.amount),
                    balance_before=float(transaction.balance_before),
                    balance_after=float(transaction.balance_after),
                    description=transaction.description,
                    reference_id=transaction.reference_id,
                    created_at=transaction.created_at
                )
                for transaction in transactions
            ]
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting transactions for wallet {wallet_uuid}: {e}")
            raise
    
    def get_wallets_by_status(
        self, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[WalletResponse]:
        """Get wallets by status."""
        try:
            wallets = self.wallet_repo.get_wallets_by_status(
                status=status,
                skip=skip,
                limit=limit
            )
            
            return [
                WalletResponse(
                    uuid=wallet.uuid,
                    balance=float(wallet.balance),
                    currency=wallet.currency,
                    status=wallet.status,
                    created_at=wallet.created_at,
                    updated_at=wallet.updated_at
                )
                for wallet in wallets
            ]
        except Exception as e:
            logger.error(f"Error getting wallets by status {status}: {e}")
            raise
    
    def validate_wallet_uuid(self, wallet_uuid: str) -> bool:
        """Validate wallet UUID format."""
        try:
            uuid.UUID(wallet_uuid)
            return True
        except ValueError:
            return False
    
    def get_wallet_statistics(self, wallet_uuid: str) -> dict:
        """Get wallet statistics."""
        try:
            wallet = self.wallet_repo.get_by_uuid_or_404(wallet_uuid)
            transactions = self.wallet_repo.get_wallet_transactions(wallet_uuid)
            
            total_deposits = sum(
                float(t.amount) for t in transactions 
                if t.operation_type == "DEPOSIT"
            )
            total_withdrawals = sum(
                float(t.amount) for t in transactions 
                if t.operation_type == "WITHDRAW"
            )
            
            return {
                "wallet_uuid": wallet_uuid,
                "current_balance": float(wallet.balance),
                "total_deposits": total_deposits,
                "total_withdrawals": total_withdrawals,
                "transaction_count": len(transactions),
                "created_at": wallet.created_at,
                "last_activity": wallet.updated_at
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet statistics {wallet_uuid}: {e}")
            raise
