from sqlalchemy.orm import Session
from sqlalchemy import select, update
from decimal import Decimal
from .models import Wallet
from .schemas import WalletOperation
from sqlalchemy.exc import NoResultFound

def get_wallet(db: Session, wallet_id):
    stmt = select(Wallet).where(Wallet.id == wallet_id)
    wallet = db.execute(stmt).scalar_one_or_none()
    return wallet

def perform_operation(db: Session, wallet_id, operation: WalletOperation):
    # Используем транзакцию с блокировкой строки для конкурентной среды
    wallet = db.execute(
        select(Wallet).where(Wallet.id == wallet_id).with_for_update()
    ).scalar_one_or_none()

    if not wallet:
        raise NoResultFound("Wallet not found")

    if operation.operation_type == "DEPOSIT":
        wallet.balance += operation.amount
    elif operation.operation_type == "WITHDRAW":
        if wallet.balance < operation.amount:
            raise ValueError("Insufficient funds")
        wallet.balance -= operation.amount
    else:
        raise ValueError("Invalid operation type")

    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet