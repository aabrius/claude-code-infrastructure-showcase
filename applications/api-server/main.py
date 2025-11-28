"""
FastAPI application for Google Ad Manager API.

This module creates and configures the FastAPI application with all routes,
middleware, and error handlers.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any, Optional
import os

from gam_api.config import get_config, Config
from gam_api.exceptions import GAMError, ValidationError, AuthenticationError
from gam_shared.logger import get_structured_logger
from routes import reports, metadata, health
from auth import get_api_key_auth
from models import ErrorResponse

logger = get_structured_logger('api')


def create_app(config: Optional[Config] = None) -> FastAPI:
    """Create and configure FastAPI application."""
    # Note: Configuration loading is deferred to allow app creation without valid config
    # This is useful for testing and documentation generation
    
    # Create FastAPI app
    app = FastAPI(
        title="Google Ad Manager API Service",
        description="RESTful API service for Google Ad Manager operations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    )
    
    # Include routers
    app.include_router(
        reports.router, 
        prefix="/api/v1/reports", 
        tags=["reports"],
        dependencies=[Depends(get_api_key_auth)]
    )
    app.include_router(
        metadata.router, 
        prefix="/api/v1/metadata", 
        tags=["metadata"],
        dependencies=[Depends(get_api_key_auth)]
    )
    app.include_router(
        health.router, 
        prefix="/api/v1", 
        tags=["health"]
    )
    
    # Global exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc):
        logger.logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="validation_error",
                message=str(exc),
                details=exc.details if hasattr(exc, 'details') else None
            ).dict()
        )
    
    @app.exception_handler(AuthenticationError)
    async def auth_exception_handler(request, exc):
        logger.logger.warning(f"Authentication error: {exc}")
        return JSONResponse(
            status_code=401,
            content=ErrorResponse(
                error="authentication_error",
                message=str(exc)
            ).dict()
        )
    
    @app.exception_handler(GAMError)
    async def gam_exception_handler(request, exc):
        logger.logger.error(f"GAM error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="gam_error",
                message=str(exc)
            ).dict()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="http_error",
                message=exc.detail
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                message="An unexpected error occurred"
            ).dict()
        )
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.logger.info("Starting Google Ad Manager API service")
        
        # Test GAM connection
        try:
            from ..core.auth import get_auth_manager
            from ..core.client import get_gam_client
            
            auth_manager = get_auth_manager()
            auth_manager.validate_config()
            
            client = get_gam_client()
            client.test_connection()
            
            logger.logger.info("GAM connection test successful")
        except Exception as e:
            logger.logger.warning(f"GAM connection test failed: {e}")
            logger.logger.warning("API starting anyway - authentication will be tested per request")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.logger.info("Shutting down Google Ad Manager API service")
    
    return app


# Create the app instance only when needed
# This prevents config loading during import
app = None

def get_app():
    """Get or create the FastAPI app instance."""
    global app
    if app is None:
        app = create_app()
    return app


def main():
    """Main entry point for running the API server."""
    config = get_config()
    
    # Configure logging
    from ..utils.logger import setup_logging
    setup_logging(level="INFO", log_file="api.log")
    
    # Get host and port
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    # Create app with loaded config before running
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()