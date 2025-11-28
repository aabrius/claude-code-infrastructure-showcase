"""
Health check and status API endpoints.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
import sys
import os

from models import HealthResponse, StatusResponse, SuccessResponse
from auth import AuthManager
from gam_api.config import get_config
from gam_shared.logger import get_structured_logger

logger = get_structured_logger('api_health')
router = APIRouter()

# Track startup time for uptime calculation
startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns the overall health status of the API and its components.
    This endpoint does not require authentication.
    """
    try:
        logger.log_function_call("health_check")
        
        # Test GAM connection
        gam_status = "unknown"
        try:
            from gam_api.auth import get_auth_manager
            from gam_api.client import get_gam_client
            
            auth_manager = get_auth_manager()
            auth_manager.validate_config()
            
            client = get_gam_client()
            client.test_connection()
            
            gam_status = "healthy"
        except Exception as e:
            logger.logger.warning(f"GAM connection test failed in health check: {e}")
            gam_status = "unhealthy"
        
        # Component status
        components = {
            "api": "healthy",
            "gam_connection": gam_status,
            "configuration": "healthy",
            "logging": "healthy"
        }
        
        # Overall status
        overall_status = "healthy" if gam_status == "healthy" else "degraded"
        
        response = HealthResponse(
            status=overall_status,
            gam_connection=gam_status,
            components=components
        )
        
        return response
        
    except Exception as e:
        logger.logger.error(f"Health check failed: {e}")
        # Return unhealthy status but don't raise exception
        return HealthResponse(
            status="unhealthy",
            gam_connection="error",
            components={
                "api": "unhealthy",
                "gam_connection": "error",
                "configuration": "unknown",
                "logging": "unknown"
            }
        )


@router.get("/status", response_model=StatusResponse)
async def detailed_status():
    """
    Detailed status endpoint with comprehensive system information.
    
    This endpoint does not require authentication but provides more
    detailed information than the basic health check.
    """
    try:
        logger.log_function_call("detailed_status")
        
        auth_manager = AuthManager()
        
        # API status
        api_status = "running"
        
        # GAM status
        gam_status = "healthy" if auth_manager.validate_gam_auth() else "unhealthy"
        
        # Authentication status
        auth_status_details = auth_manager.get_auth_status()
        auth_status = "healthy" if auth_status_details.get("gam_auth") == "valid" else "unhealthy"
        
        # Configuration status
        config_status = "healthy" if auth_status_details.get("config_loaded") else "unhealthy"
        
        # Calculate uptime
        uptime = time.time() - startup_time
        
        response = StatusResponse(
            api_status=api_status,
            gam_status=gam_status,
            auth_status=auth_status,
            config_status=config_status,
            uptime=uptime
        )
        
        logger.logger.info("Status check completed successfully")
        return response
        
    except Exception as e:
        logger.logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@router.get("/version", response_model=SuccessResponse)
async def get_version():
    """
    Get API version and system information.
    """
    try:
        version_info = {
            "api_version": "1.0.0",
            "python_version": sys.version,
            "platform": sys.platform,
            "startup_time": datetime.fromtimestamp(startup_time).isoformat(),
            "uptime_seconds": time.time() - startup_time
        }
        
        response = SuccessResponse(
            message="Version information retrieved successfully",
            data=version_info
        )
        
        return response
        
    except Exception as e:
        logger.logger.error(f"Error getting version info: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve version information")