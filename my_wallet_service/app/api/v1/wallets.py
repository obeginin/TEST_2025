from my_wallet_service.utils.database import get_db
from my_wallet_service.app.schemas import schema
from my_wallet_service.app.crud import service

from fastapi import APIRouter, Depends,Form, Request, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from uuid import UUID
import logging
logger = logging.getLogger(__name__)

# Include API routers
wallets_router = APIRouter()

# /api/v1/wallets/{wallet_id}/operation
@wallets_router.post("/wallets/{wallet_id}/operation", response_model=schema.WalletResponse)
def wallet_operation(wallet_id: UUID, operation: schema.WalletOperation, db: Session = Depends(get_db)):
    try:
        wallet = service.perform_operation(db, wallet_id, operation)
        return wallet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="Wallet not found")

# /api/v1/wallets/{wallet_id}
@wallets_router.get("/wallets/{wallet_id}", response_model=schema.WalletResponse)
def get_wallet(wallet_id: UUID, db: Session = Depends(get_db)):
    wallet = service.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet