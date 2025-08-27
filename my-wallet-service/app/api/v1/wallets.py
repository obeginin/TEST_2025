from fastapi import APIRouter, Depends,Form, Request, HTTPException, status, Response, Query, HTTPException, Depends
from uuid import UUID
from ..config import settings

from sqlalchemy.orm import Session
from ..schemas import schemas
from ..CRUD import services
# Include API routers

wallets_router = APIRouter(prefix="/api/auth", tags=["auth"])


@wallets_router.post("/api/v1/wallets/{wallet_id}/operation", response_model=schemas.WalletResponse)
def wallet_operation(wallet_id: UUID, operation: schemas.WalletOperation, db: Session = Depends(get_db)):
    try:
        wallet = services.perform_operation(db, wallet_id, operation)
        return wallet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="Wallet not found")

@wallets_router.get("/api/v1/wallets/{wallet_id}", response_model=schemas.WalletResponse)
def get_wallet(wallet_id: UUID, db: Session = Depends(get_db)):
    wallet = services.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet