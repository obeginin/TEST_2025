from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Any, List, Dict
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    
    success: bool = Field(default=True, description="Request success status")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[T] = Field(default=None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class ErrorResponse(BaseModel):
    """Error response wrapper."""
    
    success: bool = Field(default=False, description="Request success status")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(description="API version")
    environment: str = Field(description="Environment name")
    database: str = Field(description="Database status")
    redis: Optional[str] = Field(default=None, description="Redis status")
    kafka: Optional[str] = Field(default=None, description="Kafka status")


# Helper functions for creating responses
def success_response(
    data: Optional[T] = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> APIResponse[T]:
    """Create a success response."""
    return APIResponse(
        success=True,
        message=message,
        data=data,
        request_id=request_id
    )


def error_response(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create an error response."""
    return ErrorResponse(
        success=False,
        message=message,
        details=details,
        request_id=request_id
    )


def paginated_response(
    items: List[T],
    total: int,
    page: int,
    size: int
) -> PaginatedResponse[T]:
    """Create a paginated response."""
    pages = (total + size - 1) // size  # Ceiling division
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
