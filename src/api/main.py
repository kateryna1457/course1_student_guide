"""
Головний FastAPI додаток.

REST API для довідника студентів.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from psycopg2 import Error as PostgresError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import get_settings
from src.constants import RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD
from src.utils import ValidationError
from src.api.exceptions import (
    validation_error_handler,
    value_error_handler,
    postgres_error_handler,
    request_validation_error_handler,
    general_exception_handler
)
from src.api.routes import students, reference

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Отримати налаштування
settings = get_settings()

# Створити rate limiter
limiter = Limiter(key_func=get_remote_address)

# Створити FastAPI додаток
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API для управління довідником студентів",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Hide schemas section by default
)

# Add rate limiter to app state
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(PostgresError, postgres_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers with API versioning (v1)
API_V1_PREFIX = f"{settings.api_prefix}/v1"
app.include_router(students.router, prefix=API_V1_PREFIX)
app.include_router(reference.router, prefix=API_V1_PREFIX)

# Keep backward compatibility - also mount on /api without version
app.include_router(students.router, prefix=settings.api_prefix, tags=["students (legacy)"])
app.include_router(reference.router, prefix=settings.api_prefix, tags=["reference (legacy)"])


@app.get("/", tags=["root"])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}")
async def root(request: Request):
    """
    Root endpoint.

    Returns:
        dict: Інформація про API
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "api_version": "v1",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "students_v1": f"{API_V1_PREFIX}/students",
            "reference_v1": f"{API_V1_PREFIX}/reference",
            "students_legacy": f"{settings.api_prefix}/students",
            "reference_legacy": f"{settings.api_prefix}/reference"
        },
        "rate_limit": f"{RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD}"
    }


@app.get("/health", tags=["health"])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}")
async def health_check(request: Request):
    """
    Health check endpoint.

    Returns:
        dict: Статус здоров'я API
    """
    from src.repositories import get_db

    db = get_db()
    db_status = "ok" if db.test_connection() else "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": settings.app_version,
        "api_version": "v1"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Подія при запуску додатка."""
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} (API v1)")
    logger.info("=" * 60)
    logger.info(f"📚 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"🔍 ReDoc: http://{settings.api_host}:{settings.api_port}/redoc")
    logger.info(f"🏥 Health: http://{settings.api_host}:{settings.api_port}/health")
    logger.info(f"🛡️  Rate Limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD}")
    logger.info("=" * 60)

    # Test database connection
    from src.repositories import get_db

    db = get_db()
    if db.test_connection():
        logger.info("✓ Database connection: OK")
    else:
        logger.error("✗ Database connection: FAILED")

    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Подія при зупинці додатка."""
    logger.info("=" * 60)
    logger.info("🛑 Shutting down...")

    # Close database connection
    from src.repositories import get_db

    db = get_db()
    db.close()

    logger.info("✓ Database connection closed")
    logger.info("=" * 60)
