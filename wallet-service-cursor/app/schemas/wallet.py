from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
from .common import BaseSchema


class OperationType(str, Enum):
    """Operation types for wallet transactions."""
    
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletResponse(BaseSchema):
    """Wallet response schema."""
    
    uuid: str = Field(..., description="Wallet UUID")
    balance: float = Field(..., description="Current balance")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Wallet status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class WalletCreate(BaseSchema):
    """Wallet creation request schema."""
    
    uuid: Optional[str] = Field(None, description="Custom wallet UUID (optional)")
    initial_balance: float = Field(default=0.0, ge=0, description="Initial balance")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    
    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v):
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {v}")
        return v


class WalletOperationRequest(BaseSchema):
    """Wallet operation request schema."""
    
    operation_type: OperationType = Field(..., description="Operation type (DEPOSIT or WITHDRAW)")
    amount: float = Field(..., gt=0, description="Operation amount")
    description: Optional[str] = Field(None, description="Operation description")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        if v > 999999999.99:  # Max 15 digits with 2 decimal places
            raise ValueError("Amount too large")
        return round(v, 2)  # Round to 2 decimal places


class WalletOperationResponse(BaseSchema):
    """Wallet operation response schema."""
    
    wallet_uuid: str = Field(..., description="Wallet UUID")
    operation_type: OperationType = Field(..., description="Operation type")
    amount: float = Field(..., description="Operation amount")
    balance_before: float = Field(..., description="Balance before operation")
    balance_after: float = Field(..., description="Balance after operation")
    transaction_id: int = Field(..., description="Transaction ID")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    created_at: datetime = Field(..., description="Operation timestamp")


class TransactionResponse(BaseSchema):
    """Transaction response schema."""
    
    id: int = Field(..., description="Transaction ID")
    wallet_id: int = Field(..., description="Wallet ID")
    operation_type: str = Field(..., description="Operation type")
    amount: float = Field(..., description="Transaction amount")
    balance_before: float = Field(..., description="Balance before transaction")
    balance_after: float = Field(..., description="Balance after transaction")
    description: Optional[str] = Field(None, description="Transaction description")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    created_at: datetime = Field(..., description="Transaction timestamp")


class WalletBalanceResponse(BaseSchema):
    """Wallet balance response schema."""
    
    uuid: str = Field(..., description="Wallet UUID")
    balance: float = Field(..., description="Current balance")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Wallet status")
    last_updated: datetime = Field(..., description="Last update timestamp")


class WalletListResponse(BaseSchema):
    """Wallet list response schema."""
    
    wallets: List[WalletResponse] = Field(..., description="List of wallets")
    total: int = Field(..., description="Total number of wallets")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class TransactionListResponse(BaseSchema):
    """Transaction list response schema."""
    
    transactions: List[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
