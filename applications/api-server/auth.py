"""
Authentication and authorization for the API.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
import os

# Add packages to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'core', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'shared', 'src'))

from gam_api.config import get_config
from gam_api.exceptions import AuthenticationError
from gam_shared.logger import get_structured_logger

logger = get_structured_logger('api_auth')

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key_auth(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Validate API key authentication.
    
    Args:
        api_key: API key from header
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If authentication fails
    """
    # Get valid API keys from config or environment
    config = get_config()
    
    # Check environment variable first
    valid_keys_env = os.getenv("API_KEYS", "")
    if valid_keys_env:
        valid_keys = [key.strip() for key in valid_keys_env.split(",") if key.strip()]
    else:
        # Default key for development (should be changed in production)
        valid_keys = ["your-api-key-here", "dev-key-123"]
    
    # Check if API key is provided
    if not api_key:
        logger.logger.warning("API key not provided")
        raise HTTPException(
            status_code=401,
            detail="API key required. Please provide X-API-Key header."
        )
    
    # Validate API key
    if api_key not in valid_keys:
        logger.logger.warning(f"Invalid API key provided: {api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.logger.debug(f"Valid API key used: {api_key[:10]}...")
    return api_key


async def get_optional_api_key_auth(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key authentication for public endpoints.
    
    Args:
        api_key: API key from header
        
    Returns:
        Validated API key or None
    """
    if not api_key:
        return None
    
    try:
        return await get_api_key_auth(api_key)
    except HTTPException:
        return None


class AuthManager:
    """Manages authentication for API endpoints."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_structured_logger('auth_manager')
    
    def validate_gam_auth(self) -> bool:
        """
        Validate Google Ad Manager authentication.
        
        Returns:
            True if authentication is valid
        """
        try:
            from gam_api.auth import get_auth_manager
            auth_manager = get_auth_manager()
            auth_manager.validate_config()
            return True
        except Exception as e:
            self.logger.logger.error(f"GAM authentication validation failed: {e}")
            return False
    
    def get_auth_status(self) -> dict:
        """
        Get detailed authentication status.
        
        Returns:
            Dictionary with authentication status details
        """
        status = {
            "api_key_auth": "enabled",
            "gam_auth": "unknown",
            "config_loaded": False
        }
        
        # Check config loading
        try:
            config = get_config()
            status["config_loaded"] = True
        except Exception as e:
            status["config_error"] = str(e)
        
        # Check GAM authentication
        if self.validate_gam_auth():
            status["gam_auth"] = "valid"
        else:
            status["gam_auth"] = "invalid"
        
        return status