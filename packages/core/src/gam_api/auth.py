"""
Authentication module for Google Ad Manager API.
Handles OAuth2 authentication for both SOAP and REST APIs.

This module now serves as a backward compatibility layer,
importing from the new gam_core package.
"""

try:
    # Import from new package location if available
    from gam_core.auth import AuthManager, get_auth_manager
    
    # Re-export for backward compatibility
    __all__ = ["AuthManager", "get_auth_manager"]
    
except ImportError:
    # Fallback implementation if gam_core is not available
    import logging
    from typing import Optional, Tuple, Any
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    
    # Import core modules - these need to be available
    from .config import Config, get_config, load_config
    from .exceptions import AuthenticationError, ConfigurationError
    
    logger = logging.getLogger(__name__)
    
    
    class AuthManager:
        """Manages authentication for Google Ad Manager API."""
        
        def __init__(self, config_path: Optional[str] = None):
            """
            Initialize AuthManager with optional config path.
            
            Args:
                config_path: Path to configuration file. If not provided,
                            will auto-detect from available config files.
            """
            self.config_path = config_path
            self._config: Optional[Config] = None
            self._credentials: Optional[Credentials] = None
        
        @property
        def config(self) -> Config:
            """Load and cache configuration."""
            if self._config is None:
                # First try to get existing config
                self._config = get_config()
                if self._config is None:
                    # If no existing config, load from file
                    self._config = load_config(self.config_path)
                logger.info("Configuration loaded successfully")
            return self._config
        
        @property
        def network_code(self) -> str:
            """Get network code from configuration."""
            network_code = self.config.auth.network_code
            if not network_code:
                raise ConfigurationError("Network code not found in configuration")
            return network_code
        
        def get_oauth2_credentials(self) -> Credentials:
            """
            Get OAuth2 credentials for REST API.
            
            Returns:
                Google OAuth2 Credentials object.
                
            Raises:
                AuthenticationError: If credentials are missing or invalid.
            """
            if self._credentials is None:
                auth_config = self.config.auth
                
                # Check required fields
                required_fields = ['client_id', 'client_secret', 'refresh_token']
                missing_fields = []
                
                if not auth_config.client_id:
                    missing_fields.append('client_id')
                if not auth_config.client_secret:
                    missing_fields.append('client_secret')
                if not auth_config.refresh_token:
                    missing_fields.append('refresh_token')
                
                if missing_fields:
                    raise AuthenticationError(
                        f"Missing required OAuth2 credentials: {', '.join(missing_fields)}"
                    )
                
                # Create credentials object
                try:
                    self._credentials = Credentials(
                        None,  # No access token yet
                        refresh_token=auth_config.refresh_token,
                        token_uri='https://oauth2.googleapis.com/token',
                        client_id=auth_config.client_id,
                        client_secret=auth_config.client_secret
                    )
                    
                    # Refresh the access token
                    self._credentials.refresh(Request())
                    logger.info("Successfully refreshed OAuth2 access token")
                    
                except Exception as e:
                    raise AuthenticationError(f"Failed to create OAuth2 credentials: {e}")
            
            # Check if token needs refresh
            if self._credentials.expired:
                try:
                    self._credentials.refresh(Request())
                    logger.info("Refreshed expired OAuth2 access token")
                except Exception as e:
                    raise AuthenticationError(f"Failed to refresh access token: {e}")
            
            return self._credentials
        
        def get_soap_client(self):
            """
            Get authenticated SOAP API client.
            
            Returns:
                GoogleAds AdManagerClient instance.
                
            Raises:
                AuthenticationError: If client creation fails.
            """
            try:
                # Import googleads only when needed to avoid import errors
                try:
                    from googleads import ad_manager
                except ImportError:
                    raise AuthenticationError(
                        "googleads library not installed. Install with: pip install googleads"
                    )
                
                # For SOAP client, we need to create a legacy-compatible YAML format
                # The googleads library requires the old format
                import tempfile
                import yaml
                
                auth_config = self.config.auth
                legacy_data = {
                    'ad_manager': {
                        'application_name': 'GAM API Tool',
                        'network_code': auth_config.network_code,
                        'client_id': auth_config.client_id,
                        'client_secret': auth_config.client_secret,
                        'refresh_token': auth_config.refresh_token
                    }
                }
                
                # Create temporary file for legacy SOAP client
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    yaml.dump(legacy_data, f)
                    temp_config_path = f.name
                
                try:
                    client = ad_manager.AdManagerClient.LoadFromStorage(temp_config_path)
                    logger.info("Successfully created SOAP API client")
                    return client
                finally:
                    # Clean up temp file
                    import os
                    os.unlink(temp_config_path)
                    
            except Exception as e:
                raise AuthenticationError(f"Failed to create SOAP API client: {e}")
        
        def get_credentials_and_network(self) -> Tuple[Credentials, str]:
            """
            Get both OAuth2 credentials and network code.
            Convenience method for REST API usage.
            
            Returns:
                Tuple of (Credentials, network_code)
            """
            return self.get_oauth2_credentials(), self.network_code
        
        def validate_config(self) -> bool:
            """
            Validate that all required configuration is present.
            
            Returns:
                True if configuration is valid.
                
            Raises:
                ConfigurationError: If configuration is invalid.
            """
            try:
                # Check that config loads
                config = self.config
                
                # Validate auth configuration
                auth_config = config.auth
                if not auth_config.network_code:
                    raise ConfigurationError("Missing network_code in configuration")
                if not auth_config.client_id:
                    raise ConfigurationError("Missing client_id in configuration")
                if not auth_config.client_secret:
                    raise ConfigurationError("Missing client_secret in configuration")
                if not auth_config.refresh_token:
                    raise ConfigurationError("Missing refresh_token in configuration")
                
                logger.info("Configuration validation successful")
                return True
                
            except Exception as e:
                logger.error(f"Configuration validation failed: {e}")
                raise
    
    
    def get_auth_manager(config_path: Optional[str] = None) -> AuthManager:
        """
        Get AuthManager instance (singleton pattern).
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            AuthManager instance
        """
        return AuthManager(config_path)
    
    
    # Re-export for backward compatibility (moved to top of except block)