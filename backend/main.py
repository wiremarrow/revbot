"""
Main FastAPI application for RevBot backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.api.routes import router
from app.core.logging import get_logger
from app.api.exceptions import (
    RevBotException,
    revitai_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from config.config import settings
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(
        "Starting RevBot backend",
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
    yield
    # Shutdown
    logger.info("Shutting down RevBot backend")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="AI-powered code generation for Autodesk Revit",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RevBotException, revitai_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "version": settings.api_version,
        "description": "AI-powered code generation for Autodesk Revit",
        "endpoints": {
            "generate": "/api/v1/generate",
            "execute": "/api/v1/execute",
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
            "tools": "/api/v1/tools"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )