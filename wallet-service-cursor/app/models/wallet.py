from sqlalchemy import Integer, String, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from .base import Base, TimestampMixin


class Wallet(Base, TimestampMixin):
    """Wallet model for storing wallet information and balance."""
    
    __tablename__ = "wallets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    balance: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # For optimistic locking
    
    # Relationships
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wallet(id={self.id}, uuid='{self.uuid}', balance={self.balance})>"


class Transaction(Base, TimestampMixin):
    """Transaction model for tracking wallet operations."""
    
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(Integer, ForeignKey("wallets.id"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # DEPOSIT, WITHDRAW
    amount: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    balance_before: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    balance_after: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, wallet_id={self.wallet_id}, type='{self.operation_type}', amount={self.amount})>"
