"""
Authentication management for the GAM SDK with fluent interface.

Provides chainable methods for authentication operations including
OAuth2 flows, token management, and credential validation.
"""

import logging
import webbrowser
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta

from gam_api.config import Config
from gam_api.auth import AuthManager as CoreAuthManager
from gam_api.exceptions import AuthenticationError
from .exceptions import AuthError, NetworkError

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Fluent authentication manager for GAM SDK.
    
    Provides chainable methods for authentication operations:
    - OAuth2 flows and token management
    - Credential validation and refresh
    - Connection testing
    - Status monitoring
    
    Usage:
        auth = (client
            .auth()
            .check_status()
            .refresh_if_needed()
            .test_connection())
    """
    
    def __init__(self, config: Config, core_auth_manager: CoreAuthManager):
        """
        Initialize authentication manager.
        
        Args:
            config: GAM configuration
            core_auth_manager: Core authentication manager
        """
        self._config = config
        self._core_auth = core_auth_manager
        self._status = None
        self._last_check = None
        self._credentials = None
    
    def check_status(self) -> 'AuthManager':
        """
        Check current authentication status.
        
        Returns:
            Self for chaining
            
        Updates internal status that can be retrieved with get_status()
        """
        try:
            self._status = {
                'authenticated': False,
                'credentials_present': False,
                'credentials_expired': None,
                'token_expiry': None,
                'last_check': datetime.now().isoformat(),
                'errors': []
            }
            
            # Check if credentials exist
            try:
                self._credentials = self._core_auth.get_oauth2_credentials()
                if self._credentials:
                    self._status['credentials_present'] = True
                    self._status['credentials_expired'] = self._credentials.expired
                    self._status['token_expiry'] = self._credentials.expiry.isoformat() if self._credentials.expiry else None
                    
                    if not self._credentials.expired:
                        self._status['authenticated'] = True
                    else:
                        self._status['errors'].append('Credentials are expired')
                else:
                    self._status['errors'].append('No credentials found')
                    
            except Exception as e:
                self._status['errors'].append(f'Credential check failed: {e}')
            
            self._last_check = datetime.now()
            logger.info(f"Authentication status checked: {self._status['authenticated']}")
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            self._status = {
                'authenticated': False,
                'credentials_present': False,
                'credentials_expired': None,
                'token_expiry': None,
                'last_check': datetime.now().isoformat(),
                'errors': [f'Status check failed: {e}']
            }
        
        return self
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get last authentication status.
        
        Returns:
            Status dictionary or None if not checked
        """
        return self._status
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            True if authenticated
        """
        if not self._status or not self._last_check:
            self.check_status()
        
        # Re-check if status is old (> 5 minutes)
        if self._last_check and datetime.now() - self._last_check > timedelta(minutes=5):
            self.check_status()
        
        return self._status.get('authenticated', False) if self._status else False
    
    def refresh_if_needed(self, force: bool = False) -> 'AuthManager':
        """
        Refresh credentials if needed or forced.
        
        Args:
            force: Force refresh even if not expired
            
        Returns:
            Self for chaining
            
        Raises:
            AuthError: If refresh fails
        """
        try:
            if not self._credentials:
                self.check_status()
            
            if not self._credentials:
                raise AuthError("No credentials available to refresh")
            
            needs_refresh = force or self._credentials.expired
            
            if needs_refresh:
                logger.info("Refreshing OAuth2 credentials")
                self._credentials.refresh(self._core_auth._get_request())
                
                # Update status
                self.check_status()
                
                if not self.is_authenticated():
                    raise AuthError("Credential refresh failed")
                
                logger.info("Credentials refreshed successfully")
            else:
                logger.info("Credentials are still valid, no refresh needed")
            
        except Exception as e:
            raise AuthError(f"Failed to refresh credentials: {e}") from e
        
        return self
    
    def login(self, 
              redirect_uri: str = 'http://localhost:8080',
              open_browser: bool = True,
              wait_for_callback: bool = False) -> 'AuthManager':
        """
        Perform OAuth2 login flow.
        
        Args:
            redirect_uri: OAuth2 redirect URI
            open_browser: Whether to open browser automatically
            wait_for_callback: Whether to wait for callback (requires local server)
            
        Returns:
            Self for chaining
            
        Raises:
            AuthError: If login fails
        """
        try:
            from google_auth_oauthlib.flow import Flow
            
            # Create OAuth2 flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self._config.auth.client_id,
                        "client_secret": self._config.auth.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                scopes=[
                    'https://www.googleapis.com/auth/dfp',
                    'https://www.googleapis.com/auth/admanager'
                ]
            )
            flow.redirect_uri = redirect_uri
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            if open_browser:
                try:
                    webbrowser.open(auth_url)
                    logger.info("Browser opened for authorization")
                except Exception:
                    logger.warning("Could not open browser automatically")
            
            if wait_for_callback:
                # TODO: Implement local server for callback
                raise NotImplementedError("Callback server not yet implemented")
            else:
                # Manual code entry
                logger.info(f"Authorization URL: {auth_url}")
                raise AuthError(
                    "Manual authorization required. "
                    "Please visit the authorization URL and provide the code."
                )
        
        except Exception as e:
            raise AuthError(f"Login flow failed: {e}") from e
    
    def logout(self, revoke_token: bool = False) -> 'AuthManager':
        """
        Logout and clear stored credentials.
        
        Args:
            revoke_token: Whether to revoke the token with Google
            
        Returns:
            Self for chaining
        """
        try:
            if revoke_token and self._credentials:
                # Revoke token with Google
                try:
                    import requests
                    revoke_url = f"https://oauth2.googleapis.com/revoke?token={self._credentials.refresh_token}"
                    response = requests.post(revoke_url)
                    if response.status_code == 200:
                        logger.info("Token revoked successfully")
                    else:
                        logger.warning(f"Token revocation failed: HTTP {response.status_code}")
                except Exception as e:
                    logger.warning(f"Token revocation failed: {e}")
            
            # Clear local credentials
            self._credentials = None
            self._status = None
            self._last_check = None
            
            logger.info("Logout completed")
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
        
        return self
    
    def test_connection(self) -> 'AuthManager':
        """
        Test connection to GAM API.
        
        Returns:
            Self for chaining
            
        Raises:
            AuthError: If not authenticated
            NetworkError: If API connection fails
        """
        try:
            if not self.is_authenticated():
                raise AuthError("Not authenticated - cannot test connection")
            
            # Test SOAP API
            soap_success = False
            soap_error = None
            try:
                soap_client = self._core_auth.get_soap_client()
                network_service = soap_client.GetService('NetworkService')
                current_network = network_service.getCurrentNetwork()
                soap_success = True
                logger.info(f"SOAP API connection successful: {current_network.get('displayName', 'Unknown')}")
            except Exception as e:
                soap_error = str(e)
                logger.warning(f"SOAP API connection failed: {e}")
            
            # Test REST API
            rest_success = False
            rest_error = None
            try:
                rest_session = self._core_auth.get_rest_session()
                network_code = self._config.auth.network_code
                url = f"https://admanager.googleapis.com/v1/networks/{network_code}"
                response = rest_session.get(url)
                if response.status_code == 200:
                    rest_success = True
                    logger.info("REST API connection successful")
                else:
                    rest_error = f"HTTP {response.status_code}"
                    logger.warning(f"REST API connection failed: {rest_error}")
            except Exception as e:
                rest_error = str(e)
                logger.warning(f"REST API connection failed: {e}")
            
            # Check if at least one API works
            if not soap_success and not rest_success:
                errors = []
                if soap_error:
                    errors.append(f"SOAP: {soap_error}")
                if rest_error:
                    errors.append(f"REST: {rest_error}")
                
                raise NetworkError(f"Both API connections failed: {'; '.join(errors)}")
            
            logger.info("API connection test passed")
            
        except AuthError:
            raise
        except NetworkError:
            raise
        except Exception as e:
            raise NetworkError(f"Connection test failed: {e}") from e
        
        return self
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get information about the connected GAM network.
        
        Returns:
            Network information dictionary
            
        Raises:
            AuthError: If not authenticated
            NetworkError: If API call fails
        """
        try:
            if not self.is_authenticated():
                raise AuthError("Not authenticated")
            
            # Try SOAP API first
            try:
                soap_client = self._core_auth.get_soap_client()
                network_service = soap_client.GetService('NetworkService')
                current_network = network_service.getCurrentNetwork()
                
                return {
                    'source': 'soap',
                    'id': current_network.get('id'),
                    'networkCode': current_network.get('networkCode'),
                    'displayName': current_network.get('displayName'),
                    'timeZone': current_network.get('timeZone'),
                    'currencyCode': current_network.get('currencyCode'),
                    'effectiveRootAdUnitId': current_network.get('effectiveRootAdUnitId'),
                    'isTest': current_network.get('isTest', False)
                }
                
            except Exception as soap_error:
                # Try REST API as fallback
                try:
                    rest_session = self._core_auth.get_rest_session()
                    network_code = self._config.auth.network_code
                    url = f"https://admanager.googleapis.com/v1/networks/{network_code}"
                    response = rest_session.get(url)
                    
                    if response.status_code == 200:
                        network_data = response.json()
                        return {
                            'source': 'rest',
                            **network_data
                        }
                    else:
                        raise NetworkError(f"REST API failed: HTTP {response.status_code}")
                        
                except Exception as rest_error:
                    raise NetworkError(
                        f"Failed to get network info from both APIs. "
                        f"SOAP: {soap_error}, REST: {rest_error}"
                    )
                    
        except (AuthError, NetworkError):
            raise
        except Exception as e:
            raise NetworkError(f"Failed to get network info: {e}") from e
    
    def validate_scopes(self, required_scopes: Optional[list] = None) -> 'AuthManager':
        """
        Validate that credentials have required scopes.
        
        Args:
            required_scopes: List of required scopes (uses default GAM scopes if None)
            
        Returns:
            Self for chaining
            
        Raises:
            AuthError: If scopes are missing
        """
        if required_scopes is None:
            required_scopes = [
                'https://www.googleapis.com/auth/dfp',
                'https://www.googleapis.com/auth/admanager'
            ]
        
        try:
            if not self._credentials:
                self.check_status()
            
            if not self._credentials:
                raise AuthError("No credentials available for scope validation")
            
            if hasattr(self._credentials, 'scopes') and self._credentials.scopes:
                missing_scopes = set(required_scopes) - set(self._credentials.scopes)
                if missing_scopes:
                    raise AuthError(f"Missing required scopes: {', '.join(missing_scopes)}")
            else:
                logger.warning("Cannot verify scopes - scope information not available")
            
            logger.info("Scope validation passed")
            
        except AuthError:
            raise
        except Exception as e:
            raise AuthError(f"Scope validation failed: {e}") from e
        
        return self
    
    def schedule_refresh(self, callback: Callable[[], None], minutes_before_expiry: int = 5) -> 'AuthManager':
        """
        Schedule automatic token refresh before expiry.
        
        Args:
            callback: Function to call after refresh
            minutes_before_expiry: Minutes before expiry to refresh
            
        Returns:
            Self for chaining
            
        Note:
            This is a placeholder for future implementation.
            Currently logs the schedule request.
        """
        logger.info(f"Token refresh scheduled {minutes_before_expiry} minutes before expiry")
        # TODO: Implement actual scheduling mechanism
        return self
    
    def __repr__(self) -> str:
        """String representation."""
        status = "authenticated" if self.is_authenticated() else "not authenticated"
        return f"AuthManager({status})"