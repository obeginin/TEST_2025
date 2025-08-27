from my_wallet_service.utils.config import settings
from my_wallet_service.app.api import api_router
from my_wallet_service.utils import database
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import asyncio
import logging
import uuid


#from .core.database import check_database_connection
#from .core.exceptions import AppException, to_http_exception


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

app.include_router(api_router, prefix=settings.api_prefix)


'''@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )'''

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



