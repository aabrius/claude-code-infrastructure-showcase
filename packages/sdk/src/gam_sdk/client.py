"""
Main SDK client for Google Ad Manager API operations.

Provides the primary entry point for all SDK functionality with
a fluent, chainable interface design.
"""

import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

from gam_api.config import get_config, Config
from gam_api.auth import AuthManager
from gam_api.exceptions import ConfigurationError, AuthenticationError
from .exceptions import SDKError, ConfigError, AuthError
from .reports import ReportBuilder
from .config import ConfigManager
from .auth import AuthManager as SDKAuthManager

logger = logging.getLogger(__name__)


class GAMClient:
    """
    Main Google Ad Manager API SDK client.
    
    Provides fluent interface for all GAM operations including:
    - Report generation and management
    - Configuration management
    - Authentication handling
    - Data export and formatting
    
    Usage:
        # Basic initialization
        client = GAMClient()
        
        # With custom config
        client = GAMClient(config_path='/path/to/config.yaml')
        
        # With config dict
        client = GAMClient(config={
            'gam': {'network_code': '12345678'},
            'oauth2': {'client_id': '...', 'client_secret': '...'}
        })
        
        # Fluent report generation
        report = (client
            .reports()
            .delivery()
            .last_7_days()
            .dimensions('DATE', 'AD_UNIT_NAME')
            .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
            .execute())
    """
    
    def __init__(self, 
                 config_path: Optional[Union[str, Path]] = None,
                 config: Optional[Dict[str, Any]] = None,
                 network_code: Optional[str] = None,
                 auto_authenticate: bool = True):
        """
        Initialize GAM SDK client.
        
        Args:
            config_path: Path to configuration file
            config: Configuration dictionary (alternative to config_path)
            network_code: GAM network code (overrides config)
            auto_authenticate: Whether to authenticate automatically on first API call
            
        Raises:
            ConfigError: If configuration cannot be loaded
            AuthError: If auto_authenticate is True and authentication fails
        """
        self._config = None
        self._auth_manager = None
        self._config_manager = None
        self._sdk_auth_manager = None
        self._authenticated = False
        self._auto_authenticate = auto_authenticate
        
        try:
            # Load configuration
            if config:
                # TODO: Implement config dict loading
                raise NotImplementedError("Config dict loading not yet implemented")
            elif config_path:
                self._config = get_config(str(config_path))
            else:
                self._config = get_config()
            
            # Override network code if provided
            if network_code:
                # Create new config with updated network code
                # TODO: Implement config override
                pass
            
            # Initialize core auth manager
            self._auth_manager = AuthManager(self._config)
            
            # Pre-authenticate if requested
            if auto_authenticate:
                self._ensure_authenticated()
                
        except ConfigurationError as e:
            raise ConfigError(f"Failed to load configuration: {e}") from e
        except AuthenticationError as e:
            if auto_authenticate:
                raise AuthError(f"Auto-authentication failed: {e}") from e
        except Exception as e:
            raise SDKError(f"Client initialization failed: {e}") from e
    
    def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated, authenticating if necessary."""
        if self._authenticated:
            return
        
        try:
            # Test current credentials
            credentials = self._auth_manager.get_oauth2_credentials()
            if credentials and not credentials.expired:
                self._authenticated = True
                return
            
            # Try to refresh if we have a refresh token
            if credentials and credentials.refresh_token:
                credentials.refresh(self._auth_manager._get_request())
                self._authenticated = True
                return
            
            # No valid credentials available
            raise AuthError(
                "No valid authentication credentials found. "
                "Please run authentication flow first."
            )
            
        except Exception as e:
            raise AuthError(f"Authentication verification failed: {e}") from e
    
    @property
    def network_code(self) -> Optional[str]:
        """Get the configured GAM network code."""
        return self._config.auth.network_code if self._config else None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        try:
            self._ensure_authenticated()
            return True
        except AuthError:
            return False
    
    def reports(self) -> ReportBuilder:
        """
        Get report builder for fluent report generation.
        
        Returns:
            ReportBuilder instance for chaining
            
        Example:
            report = (client
                .reports()
                .delivery()
                .last_30_days()
                .dimensions('DATE', 'AD_UNIT_NAME')
                .execute())
        """
        if self._auto_authenticate:
            self._ensure_authenticated()
        
        return ReportBuilder(self._config, self._auth_manager)
    
    def config(self) -> ConfigManager:
        """
        Get configuration manager for fluent config operations.
        
        Returns:
            ConfigManager instance for chaining
            
        Example:
            config = (client
                .config()
                .set('gam.network_code', '12345678')
                .set('logging.level', 'DEBUG')
                .validate())
        """
        if self._config_manager is None:
            self._config_manager = ConfigManager(self._config)
        
        return self._config_manager
    
    def auth(self) -> SDKAuthManager:
        """
        Get authentication manager for fluent auth operations.
        
        Returns:
            SDKAuthManager instance for chaining
            
        Example:
            auth_status = (client
                .auth()
                .check_status()
                .refresh_if_needed())
        """
        if self._sdk_auth_manager is None:
            self._sdk_auth_manager = SDKAuthManager(self._config, self._auth_manager)
        
        return self._sdk_auth_manager
    
    def quick_report(self, report_type: str, days_back: int = 30) -> 'ReportResult':
        """
        Generate a quick report with predefined settings.
        
        Args:
            report_type: Type of report ('delivery', 'inventory', 'sales', etc.)
            days_back: Number of days to include in the report
            
        Returns:
            ReportResult with the generated data
            
        Example:
            report = client.quick_report('delivery', days_back=7)
            report.to_csv('delivery.csv')
        """
        return (self
                .reports()
                .quick(report_type)
                .days_back(days_back)
                .execute())
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to GAM API and return status information.
        
        Returns:
            Dictionary with connection test results
            
        Raises:
            AuthError: If authentication fails
            NetworkError: If API connection fails
        """
        try:
            self._ensure_authenticated()
            
            # Test SOAP API connection
            soap_status = "unknown"
            soap_error = None
            try:
                soap_client = self._auth_manager.get_soap_client()
                network_service = soap_client.GetService('NetworkService')
                current_network = network_service.getCurrentNetwork()
                soap_status = "connected"
                network_info = {
                    'id': current_network.get('id'),
                    'networkCode': current_network.get('networkCode'),
                    'displayName': current_network.get('displayName'),
                    'timeZone': current_network.get('timeZone'),
                    'currencyCode': current_network.get('currencyCode')
                }
            except Exception as e:
                soap_status = "error"
                soap_error = str(e)
                network_info = None
            
            # Test REST API connection
            rest_status = "unknown"
            rest_error = None
            try:
                rest_session = self._auth_manager.get_rest_session()
                url = f"https://admanager.googleapis.com/v1/networks/{self.network_code}"
                response = rest_session.get(url)
                if response.status_code == 200:
                    rest_status = "connected"
                else:
                    rest_status = "error"
                    rest_error = f"HTTP {response.status_code}"
            except Exception as e:
                rest_status = "error"
                rest_error = str(e)
            
            return {
                'authenticated': True,
                'network_code': self.network_code,
                'network_info': network_info,
                'soap_api': {
                    'status': soap_status,
                    'error': soap_error
                },
                'rest_api': {
                    'status': rest_status,
                    'error': rest_error
                },
                'overall_status': 'healthy' if soap_status == 'connected' or rest_status == 'connected' else 'unhealthy'
            }
            
        except AuthError:
            return {
                'authenticated': False,
                'network_code': self.network_code,
                'network_info': None,
                'soap_api': {'status': 'unauthenticated', 'error': None},
                'rest_api': {'status': 'unauthenticated', 'error': None},
                'overall_status': 'unauthenticated'
            }
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"GAMClient(network_code='{self.network_code}', authenticated={self.is_authenticated})"
    
    def __enter__(self) -> 'GAMClient':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        # Cleanup if needed
        pass


def create_client(**kwargs) -> GAMClient:
    """
    Convenience function to create a GAM client.
    
    Args:
        **kwargs: Arguments passed to GAMClient constructor
        
    Returns:
        Configured GAMClient instance
    """
    return GAMClient(**kwargs)