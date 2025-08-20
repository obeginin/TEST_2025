from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from Database import SessionLocal, engine, Base
from . import models, schemas, crud

# Создаём таблицы (только для примера, лучше через миграции Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wallet API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/wallets/{wallet_id}/operation", response_model=schemas.WalletResponse)
def wallet_operation(wallet_id: UUID, operation: schemas.WalletOperation, db: Session = Depends(get_db)):
    try:
        wallet = crud.perform_operation(db, wallet_id, operation)
        return wallet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="Wallet not found")

@app.get("/api/v1/wallets/{wallet_id}", response_model=schemas.WalletResponse)
def get_wallet(wallet_id: UUID, db: Session = Depends(get_db)):
    wallet = crud.get_wallet(db, wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet