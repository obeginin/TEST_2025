from sqlalchemy.orm import Session
from sqlalchemy import select, update
from decimal import Decimal
from .models import Wallet
from .schemas import WalletOperation
from sqlalchemy import text



def get_wallet(db: Session, wallet_id):
    stmt = text("SELECT balance FROM wallets WHERE id = :wallet_id")
    row = db.execute(stmt, {"wallet_id": wallet_id}).fetchone()
    return row[0] if row else None

def perform_operation(db: Session, wallet_id, operation: WalletOperation):
    # Используем транзакцию с блокировкой строки для конкурентной среды
    with db.begin():
        # Блокируем строку с помощью SELECT ... FOR UPDATE
        wallet_row = db.execute(
            text("SELECT id, balance FROM wallets WHERE id = :wallet_id FOR UPDATE"),
            {"wallet_id": wallet_id}
        ).fetchone()

        if not wallet_row:
            raise ValueError("Wallet not found")

        current_balance = wallet_row.balance

        if operation.operation_type == "DEPOSIT":
            new_balance = current_balance + operation.amount
        elif operation.operation_type == "WITHDRAW":
            if current_balance < operation.amount:
                raise ValueError("Insufficient funds")
            new_balance = current_balance - operation.amount
        else:
            raise ValueError("Invalid operation type")

        # Обновляем баланс
        db.execute(
            text("UPDATE wallets SET balance = :balance WHERE id = :wallet_id"),
            {"balance": new_balance, "wallet_id": wallet_id}
        )
        db.commit()


        updated_wallet = db.execute(
            text("SELECT id, balance FROM wallets WHERE id = :wallet_id"),
            {"wallet_id": wallet_id}
        ).fetchone()

    return updated_wallet