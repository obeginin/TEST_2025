from my_wallet_service.utils.config import settings
from my_wallet_service.app.api import api_router
from my_wallet_service.utils import database
from my_wallet_service.utils.exceptions import AppException
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import asyncio
from my_wallet_service.utils.log import setup_logging  # если ты вынес код в отдельный модуль
import logging
import uuid
#from .core.database import check_database_connection
#from .core.exceptions import AppException, to_http_exception
logger = logging.getLogger(__name__)

setup_logging()  # <- настраиваем логирование




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Wallet Service API...")
    try:
        result = await asyncio.to_thread(database.check_database_connection)
        # Check database connection
        if not result:
            logger.error("❌ Database connection failed. Application may not work properly.")
    except Exception as e:
        logger.error(f"❌ Error during database check: {e}")
    logger.info("✅ Wallet Service API started successfully")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Wallet Service API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A modern wallet management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Global exception handlers (ловит все ошибка приложения)
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(f"AppException: {exc.message} (Request ID: {getattr(request.state, 'request_id', 'unknown')})")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()} (Request ID: {getattr(request.state, 'request_id', 'unknown')})")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "details": exc.errors(),
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)} (Request ID: {getattr(request.state, 'request_id', 'unknown')})")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# connecting routes
app.include_router(api_router, prefix=settings.api_prefix)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment
    }



