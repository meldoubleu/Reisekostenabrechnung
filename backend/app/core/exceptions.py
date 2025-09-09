from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from typing import Union
from .logging import logger


async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions and return JSON responses."""
    logger.error(f"HTTP {exc.status_code} error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )


async def custom_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors and return JSON responses."""
    logger.error(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "message": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


async def custom_general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions and return JSON responses."""
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "path": str(request.url.path)
        }
    )


async def custom_starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions and return JSON responses."""
    logger.error(f"Starlette HTTP {exc.status_code} error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )
