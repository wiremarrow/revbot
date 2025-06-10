"""
Custom exceptions and error handlers for the API.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

logger = structlog.get_logger(__name__)


class RevBotException(Exception):
    """Base exception for RevBot."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class CodeGenerationException(RevBotException):
    """Exception raised during code generation."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class CodeExecutionException(RevBotException):
    """Exception raised during code execution."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ValidationException(RevBotException):
    """Exception raised during validation."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


async def revitai_exception_handler(request: Request, exc: RevBotException):
    """Handle RevBot custom exceptions."""
    logger.error(
        "RevBot exception",
        exception_type=type(exc).__name__,
        message=exc.message,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": type(exc).__name__,
                "message": exc.message
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "Unexpected error",
        exception_type=type(exc).__name__,
        message=str(exc),
        path=request.url.path,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred"
            }
        }
    )