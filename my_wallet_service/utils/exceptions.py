from typing import Any, Dict, Optional
import logging
logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            status_code=404
        )


class ValidationError(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details
        )


class ConflictError(AppException):
    """Conflict error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            details=details
        )


class InsufficientFundsError(AppException):
    """Insufficient funds exception."""
    
    def __init__(self, wallet_uuid: str, requested_amount: float, current_balance: float):
        super().__init__(
            message=f"Insufficient funds in wallet {wallet_uuid}",
            status_code=400,
            details={
                "wallet_uuid": wallet_uuid,
                "requested_amount": requested_amount,
                "current_balance": current_balance
            }
        )


class InvalidOperationError(AppException):
    """Invalid operation exception."""
    
    def __init__(self, operation_type: str, message: str = None):
        super().__init__(
            message=message or f"Invalid operation type: {operation_type}",
            status_code=400,
            details={"operation_type": operation_type}
        )


def to_http_exception(exc: AppException):
    """Convert AppException to HTTPException."""
    from fastapi import HTTPException
    
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details
        }
    )
