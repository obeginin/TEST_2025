from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID

class WalletOperation(BaseModel):
    operation_type: str  # "DEPOSIT" или "WITHDRAW"
    amount: Decimal

class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal