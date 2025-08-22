from sqlalchemy.orm import Session
from sqlalchemy import select, text
from typing import List, Optional, Tuple
from .base import BaseRepository
from ..models.wallet import Wallet, Transaction
from ..core.exceptions import NotFoundError, InsufficientFundsError
import logging
import uuid

logger = logging.getLogger(__name__)


class WalletRepository(BaseRepository[Wallet]):
    """Repository for Wallet operations with concurrency support."""
    
    def __init__(self, db: Session):
        super().__init__(Wallet, db)
    
    def get_by_uuid(self, wallet_uuid: str) -> Optional[Wallet]:
        """Get wallet by UUID."""
        return self.get_by_field("uuid", wallet_uuid)
    
    def get_by_uuid_or_404(self, wallet_uuid: str) -> Wallet:
        """Get wallet by UUID or raise 404 error."""
        wallet = self.get_by_uuid(wallet_uuid)
        if not wallet:
            raise NotFoundError("Wallet", wallet_uuid)
        return wallet
    
    def get_wallet_with_lock(self, wallet_uuid: str) -> Optional[Wallet]:
        """Get wallet with row-level lock for concurrent operations."""
        try:
            # Use SELECT FOR UPDATE to lock the row
            stmt = (
                select(Wallet)
                .where(Wallet.uuid == wallet_uuid)
                .with_for_update()
            )
            return self.db.scalar(stmt)
        except Exception as e:
            logger.error(f"Error getting wallet with lock {wallet_uuid}: {e}")
            raise
    
    def create_wallet(self, wallet_uuid: str = None, initial_balance: float = 0.0) -> Wallet:
        """Create a new wallet."""
        if wallet_uuid is None:
            wallet_uuid = str(uuid.uuid4())
        else:
            # Validate UUID format if provided
            try:
                uuid.UUID(wallet_uuid)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {wallet_uuid}")
        
        # Check if wallet with this UUID already exists
        existing_wallet = self.get_by_uuid(wallet_uuid)
        if existing_wallet:
            raise ValueError(f"Wallet with UUID {wallet_uuid} already exists")
        
        return self.create(
            uuid=wallet_uuid,
            balance=initial_balance,
            currency="USD",
            status="active"
        )
    
    def update_balance(
        self, 
        wallet_uuid: str, 
        amount: float, 
        operation_type: str,
        description: str = None,
        reference_id: str = None
    ) -> Tuple[Wallet, Transaction]:
        """
        Update wallet balance with transaction logging.
        Uses row-level locking to ensure thread safety.
        """
        try:
            # Get wallet with lock
            wallet = self.get_wallet_with_lock(wallet_uuid)
            if not wallet:
                raise NotFoundError("Wallet", wallet_uuid)
            
            # Check wallet status
            if wallet.status != "active":
                raise ValueError(f"Wallet {wallet_uuid} is not active (status: {wallet.status})")
            
            # Calculate new balance
            balance_before = float(wallet.balance)
            
            if operation_type == "DEPOSIT":
                balance_after = balance_before + amount
            elif operation_type == "WITHDRAW":
                balance_after = balance_before - amount
                if balance_after < 0:
                    raise InsufficientFundsError(wallet_uuid, amount, balance_before)
            else:
                raise ValueError(f"Invalid operation type: {operation_type}")
            
            # Update wallet balance and version (optimistic locking)
            wallet.balance = balance_after
            wallet.version += 1
            
            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.id,
                operation_type=operation_type,
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=description,
                reference_id=reference_id
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(wallet)
            self.db.refresh(transaction)
            
            logger.info(
                f"Wallet {wallet_uuid} {operation_type.lower()}ed {amount}. "
                f"Balance: {balance_before} -> {balance_after}"
            )
            
            return wallet, transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating wallet balance: {e}")
            raise
    
    def get_wallet_transactions(
        self, 
        wallet_uuid: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions for a specific wallet."""
        wallet = self.get_by_uuid_or_404(wallet_uuid)
        
        stmt = (
            select(Transaction)
            .where(Transaction.wallet_id == wallet.id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(self.db.scalars(stmt).all())
    
    def get_wallet_balance(self, wallet_uuid: str) -> float:
        """Get wallet balance."""
        wallet = self.get_by_uuid_or_404(wallet_uuid)
        return float(wallet.balance)
    
    def get_wallets_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Wallet]:
        """Get wallets by status."""
        stmt = (
            select(Wallet)
            .where(Wallet.status == status)
            .order_by(Wallet.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(self.db.scalars(stmt).all())


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction operations."""
    
    def __init__(self, db: Session):
        super().__init__(Transaction, db)
    
    def get_by_reference_id(self, reference_id: str) -> Optional[Transaction]:
        """Get transaction by reference ID."""
        return self.get_by_field("reference_id", reference_id)
    
    def get_transactions_by_wallet_id(
        self, 
        wallet_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by wallet ID."""
        stmt = (
            select(Transaction)
            .where(Transaction.wallet_id == wallet_id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(self.db.scalars(stmt).all())
    
    def get_transactions_by_type(
        self, 
        operation_type: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get transactions by operation type."""
        stmt = (
            select(Transaction)
            .where(Transaction.operation_type == operation_type)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(self.db.scalars(stmt).all())
