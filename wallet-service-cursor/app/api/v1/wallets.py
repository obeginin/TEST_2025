from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...services.wallet_service import WalletService
from ...schemas.wallet import (
    WalletResponse, WalletCreate, WalletOperationRequest, WalletOperationResponse,
    TransactionResponse, WalletBalanceResponse
)
 
from ...core.exceptions import AppException, to_http_exception
from ...core.database import get_db

router = APIRouter()


def get_wallet_service(db: Session = Depends(get_db)) -> WalletService:
    """Dependency to get wallet service."""
    return WalletService(db)


@router.post("", response_model=WalletResponse)
async def create_wallet(
    wallet_data: WalletCreate,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Create a new wallet."""
    try:
        wallet = wallet_service.create_wallet(wallet_data)
        return wallet
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wallet: {str(e)}"
        )


@router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet(
    wallet_uuid: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get wallet by UUID."""
    try:
        # Validate UUID format
        if not wallet_service.validate_wallet_uuid(wallet_uuid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet UUID format"
            )
        
        wallet = wallet_service.get_wallet(wallet_uuid)
        return wallet
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wallet: {str(e)}"
        )


@router.get("/{wallet_uuid}/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    wallet_uuid: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get wallet balance."""
    try:
        # Validate UUID format
        if not wallet_service.validate_wallet_uuid(wallet_uuid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet UUID format"
            )
        
        balance = wallet_service.get_wallet_balance(wallet_uuid)
        return balance
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wallet balance: {str(e)}"
        )


@router.post("/{wallet_uuid}/operation", response_model=WalletOperationResponse)
async def perform_wallet_operation(
    wallet_uuid: str,
    operation_data: WalletOperationRequest,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Perform wallet operation (deposit or withdraw)."""
    try:
        # Validate UUID format
        if not wallet_service.validate_wallet_uuid(wallet_uuid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet UUID format"
            )
        
        result = wallet_service.perform_operation(wallet_uuid, operation_data)
        return result
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform operation: {str(e)}"
        )


@router.get("/{wallet_uuid}/transactions", response_model=List[TransactionResponse])
async def get_wallet_transactions(
    wallet_uuid: str,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return"),
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get transactions for a specific wallet."""
    try:
        # Validate UUID format
        if not wallet_service.validate_wallet_uuid(wallet_uuid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet UUID format"
            )
        
        transactions = wallet_service.get_wallet_transactions(wallet_uuid, skip, limit)
        return transactions
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )


@router.get("/{wallet_uuid}/statistics")
async def get_wallet_statistics(
    wallet_uuid: str,
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get wallet statistics."""
    try:
        # Validate UUID format
        if not wallet_service.validate_wallet_uuid(wallet_uuid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid wallet UUID format"
            )
        
        statistics = wallet_service.get_wallet_statistics(wallet_uuid)
        return statistics
    except AppException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wallet statistics: {str(e)}"
        )
