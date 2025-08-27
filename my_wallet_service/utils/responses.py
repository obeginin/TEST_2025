from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
import logging
logger = logging.getLogger(__name__)
T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")


class SuccessResponse(BaseResponse, Generic[T]):
    """Success response model with data."""
    
    data: T = Field(..., description="Response data")
    success: bool = Field(default=True, description="Operation success status")


class ErrorResponse(BaseResponse):
    """Error response model."""
    
    success: bool = Field(default=False, description="Operation success status")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model."""
    
    data: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    success: bool = Field(default=True, description="Operation success status")


def success_response(
    data: Any,
    message: str = "Operation completed successfully"
) -> Dict[str, Any]:
    """Create a success response."""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create an error response."""
    return {
        "success": False,
        "message": message,
        "details": details,
        "request_id": request_id
    }


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    size: int,
    message: str = "Data retrieved successfully"
) -> Dict[str, Any]:
    """Create a paginated response."""
    pages = (total + size - 1) // size  # Ceiling division
    
    return {
        "success": True,
        "message": message,
        "data": data,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }
