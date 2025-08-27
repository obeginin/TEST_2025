from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import uuid
from api import wallets
from .core.config import settings
from .core.database import check_database_connection
from .core.exceptions import AppException, to_http_exception
from .api.v1.wallets import router as wallets_router
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Wallet Service API...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("❌ Database connection failed. Application may not work properly.")
    
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

app.include_router(
    app.api.v1.wallets.wallets_router,
    prefix=settings.api_prefix + "/wallets",
    tags=["Wallets"]
)




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



if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
