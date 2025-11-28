"""
Unit tests for the GAM SDK authentication module.

Tests the AuthManager class functionality including authentication status,
credential management, connection testing, and fluent interface.
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from gam_sdk.auth import AuthManager
from gam_sdk.exceptions import AuthError, NetworkError
from gam_api.exceptions import AuthenticationError


class TestAuthManagerInitialization:
    """Test AuthManager initialization."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_initialization(self, mock_config):
        """Test AuthManager initialization."""
        mock_core_auth = Mock()
        
        auth_manager = AuthManager(mock_config, mock_core_auth)
        
        assert auth_manager._config == mock_config
        assert auth_manager._core_auth == mock_core_auth
        assert auth_manager._status is None
        assert auth_manager._last_check is None
        assert auth_manager._credentials is None


class TestAuthManagerStatusChecking:
    """Test AuthManager status checking functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_check_status_with_valid_credentials(self, auth_manager, mock_oauth_credentials):
        """Test check_status with valid credentials."""
        auth_manager._core_auth.get_oauth2_credentials.return_value = mock_oauth_credentials
        
        result = auth_manager.check_status()
        
        assert result is auth_manager
        assert auth_manager._status is not None
        assert auth_manager._status['authenticated'] is True
        assert auth_manager._status['credentials_present'] is True
        assert auth_manager._status['credentials_expired'] is False
        assert len(auth_manager._status['errors']) == 0
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_check_status_with_expired_credentials(self, auth_manager, mock_oauth_credentials):
        """Test check_status with expired credentials."""
        mock_oauth_credentials.expired = True
        auth_manager._core_auth.get_oauth2_credentials.return_value = mock_oauth_credentials
        
        result = auth_manager.check_status()
        
        assert result is auth_manager
        assert auth_manager._status['authenticated'] is False
        assert auth_manager._status['credentials_present'] is True
        assert auth_manager._status['credentials_expired'] is True
        assert 'Credentials are expired' in auth_manager._status['errors']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_check_status_with_no_credentials(self, auth_manager):
        """Test check_status with no credentials."""
        auth_manager._core_auth.get_oauth2_credentials.return_value = None
        
        result = auth_manager.check_status()
        
        assert result is auth_manager
        assert auth_manager._status['authenticated'] is False
        assert auth_manager._status['credentials_present'] is False
        assert 'No credentials found' in auth_manager._status['errors']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_check_status_with_exception(self, auth_manager):
        """Test check_status with exception during credential retrieval."""
        auth_manager._core_auth.get_oauth2_credentials.side_effect = Exception("Credential error")
        
        result = auth_manager.check_status()
        
        assert result is auth_manager
        assert auth_manager._status['authenticated'] is False
        assert auth_manager._status['credentials_present'] is False
        assert any('Credential check failed' in error for error in auth_manager._status['errors'])
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_get_status(self, auth_manager):
        """Test get_status method."""
        # Before checking status
        assert auth_manager.get_status() is None
        
        # After checking status
        auth_manager._core_auth.get_oauth2_credentials.return_value = None
        auth_manager.check_status()
        
        status = auth_manager.get_status()
        assert status is not None
        assert isinstance(status, dict)
        assert 'authenticated' in status
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_is_authenticated_first_call(self, auth_manager, mock_oauth_credentials):
        """Test is_authenticated on first call (triggers check_status)."""
        auth_manager._core_auth.get_oauth2_credentials.return_value = mock_oauth_credentials
        
        result = auth_manager.is_authenticated()
        
        assert result is True
        assert auth_manager._last_check is not None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_is_authenticated_cached_recent(self, auth_manager, mock_oauth_credentials):
        """Test is_authenticated with recent cached status."""
        # Setup recent check
        auth_manager._status = {'authenticated': True}
        auth_manager._last_check = datetime.now()
        
        result = auth_manager.is_authenticated()
        
        assert result is True
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_is_authenticated_cached_old(self, auth_manager, mock_oauth_credentials):
        """Test is_authenticated with old cached status (should re-check)."""
        # Setup old check (> 5 minutes)
        auth_manager._status = {'authenticated': True}
        auth_manager._last_check = datetime.now() - timedelta(minutes=10)
        auth_manager._core_auth.get_oauth2_credentials.return_value = mock_oauth_credentials
        
        result = auth_manager.is_authenticated()
        
        assert result is True
        # Should have updated last_check
        assert auth_manager._last_check > datetime.now() - timedelta(seconds=10)


class TestAuthManagerCredentialRefresh:
    """Test AuthManager credential refresh functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_if_needed_not_needed(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed when refresh is not needed."""
        # Setup valid credentials
        mock_oauth_credentials.expired = False
        auth_manager._credentials = mock_oauth_credentials
        
        result = auth_manager.refresh_if_needed()
        
        assert result is auth_manager
        mock_oauth_credentials.refresh.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_if_needed_expired_credentials(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with expired credentials."""
        # Setup expired credentials
        mock_oauth_credentials.expired = True
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        # Mock successful refresh
        with patch.object(auth_manager, 'check_status') as mock_check, \
             patch.object(auth_manager, 'is_authenticated', return_value=True):
            
            result = auth_manager.refresh_if_needed()
            
            assert result is auth_manager
            mock_oauth_credentials.refresh.assert_called_once()
            mock_check.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_if_needed_force_refresh(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with force=True."""
        # Setup valid credentials
        mock_oauth_credentials.expired = False
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        # Mock successful refresh
        with patch.object(auth_manager, 'check_status') as mock_check, \
             patch.object(auth_manager, 'is_authenticated', return_value=True):
            
            result = auth_manager.refresh_if_needed(force=True)
            
            assert result is auth_manager
            mock_oauth_credentials.refresh.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_if_needed_no_credentials(self, auth_manager):
        """Test refresh_if_needed with no credentials."""
        auth_manager._credentials = None
        auth_manager._core_auth.get_oauth2_credentials.return_value = None
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.refresh_if_needed()
        
        assert "No credentials available to refresh" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_if_needed_refresh_failure(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with refresh failure."""
        # Setup expired credentials
        mock_oauth_credentials.expired = True
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        # Mock failed refresh
        with patch.object(auth_manager, 'check_status') as mock_check, \
             patch.object(auth_manager, 'is_authenticated', return_value=False):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.refresh_if_needed()
            
            assert "Credential refresh failed" in str(exc_info.value)


class TestAuthManagerLogin:
    """Test AuthManager login functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        # Mock config for OAuth flow
        mock_config.auth.client_id = "test_client_id"
        mock_config.auth.client_secret = "test_client_secret"
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_login_flow_setup(self, auth_manager):
        """Test login flow setup (should raise AuthError for manual authorization)."""
        with patch('src.sdk.auth.Flow') as mock_flow_class, \
             patch('src.sdk.auth.webbrowser.open') as mock_open:
            
            mock_flow = Mock()
            mock_flow.authorization_url.return_value = ("http://auth.url", "state")
            mock_flow_class.from_client_config.return_value = mock_flow
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.login()
            
            assert "Manual authorization required" in str(exc_info.value)
            mock_open.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_login_flow_no_browser(self, auth_manager):
        """Test login flow without opening browser."""
        with patch('src.sdk.auth.Flow') as mock_flow_class, \
             patch('src.sdk.auth.webbrowser.open') as mock_open:
            
            mock_flow = Mock()
            mock_flow.authorization_url.return_value = ("http://auth.url", "state")
            mock_flow_class.from_client_config.return_value = mock_flow
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.login(open_browser=False)
            
            assert "Manual authorization required" in str(exc_info.value)
            mock_open.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_login_flow_callback_not_implemented(self, auth_manager):
        """Test login flow with callback (not yet implemented)."""
        with patch('src.sdk.auth.Flow') as mock_flow_class:
            mock_flow = Mock()
            mock_flow.authorization_url.return_value = ("http://auth.url", "state")
            mock_flow_class.from_client_config.return_value = mock_flow
            
            with pytest.raises(NotImplementedError):
                auth_manager.login(wait_for_callback=True)


class TestAuthManagerLogout:
    """Test AuthManager logout functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_logout_without_token_revocation(self, auth_manager, mock_oauth_credentials):
        """Test logout without token revocation."""
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._status = {'authenticated': True}
        auth_manager._last_check = datetime.now()
        
        result = auth_manager.logout(revoke_token=False)
        
        assert result is auth_manager
        assert auth_manager._credentials is None
        assert auth_manager._status is None
        assert auth_manager._last_check is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_logout_with_token_revocation_success(self, auth_manager, mock_oauth_credentials):
        """Test logout with successful token revocation."""
        auth_manager._credentials = mock_oauth_credentials
        
        with patch('src.sdk.auth.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = auth_manager.logout(revoke_token=True)
            
            assert result is auth_manager
            assert auth_manager._credentials is None
            mock_post.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_logout_with_token_revocation_failure(self, auth_manager, mock_oauth_credentials):
        """Test logout with failed token revocation."""
        auth_manager._credentials = mock_oauth_credentials
        
        with patch('src.sdk.auth.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_post.return_value = mock_response
            
            result = auth_manager.logout(revoke_token=True)
            
            # Should still succeed (logout locally)
            assert result is auth_manager
            assert auth_manager._credentials is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_logout_with_token_revocation_exception(self, auth_manager, mock_oauth_credentials):
        """Test logout with exception during token revocation."""
        auth_manager._credentials = mock_oauth_credentials
        
        with patch('src.sdk.auth.requests.post', side_effect=Exception("Request error")):
            result = auth_manager.logout(revoke_token=True)
            
            # Should still succeed (logout locally)
            assert result is auth_manager
            assert auth_manager._credentials is None


class TestAuthManagerConnectionTesting:
    """Test AuthManager connection testing functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        mock_config.auth.network_code = "123456789"
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_test_connection_success(self, auth_manager, sample_network_info):
        """Test successful connection test (both APIs work)."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API success
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = sample_network_info
            mock_soap_client.GetService.return_value = mock_network_service
            auth_manager._core_auth.get_soap_client.return_value = mock_soap_client
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            result = auth_manager.test_connection()
            
            assert result is auth_manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_test_connection_not_authenticated(self, auth_manager):
        """Test connection test when not authenticated."""
        with patch.object(auth_manager, 'is_authenticated', return_value=False):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.test_connection()
            
            assert "Not authenticated" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_test_connection_soap_failure_rest_success(self, auth_manager):
        """Test connection test with SOAP failure but REST success."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API failure
            auth_manager._core_auth.get_soap_client.side_effect = Exception("SOAP error")
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            result = auth_manager.test_connection()
            
            assert result is auth_manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_test_connection_both_apis_fail(self, auth_manager):
        """Test connection test with both APIs failing."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API failure
            auth_manager._core_auth.get_soap_client.side_effect = Exception("SOAP error")
            
            # Mock REST API failure
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_session.get.return_value = mock_response
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            with pytest.raises(NetworkError) as exc_info:
                auth_manager.test_connection()
            
            assert "Both API connections failed" in str(exc_info.value)


class TestAuthManagerNetworkInfo:
    """Test AuthManager network information functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        mock_config.auth.network_code = "123456789"
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_get_network_info_soap_success(self, auth_manager, sample_network_info):
        """Test get_network_info with SOAP API success."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API success
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = sample_network_info
            mock_soap_client.GetService.return_value = mock_network_service
            auth_manager._core_auth.get_soap_client.return_value = mock_soap_client
            
            result = auth_manager.get_network_info()
            
            assert result['source'] == 'soap'
            assert result['id'] == sample_network_info['id']
            assert result['networkCode'] == sample_network_info['networkCode']
            assert result['displayName'] == sample_network_info['displayName']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_get_network_info_soap_fail_rest_success(self, auth_manager, sample_network_info):
        """Test get_network_info with SOAP failure but REST success."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API failure
            auth_manager._core_auth.get_soap_client.side_effect = Exception("SOAP error")
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_network_info
            mock_session.get.return_value = mock_response
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            result = auth_manager.get_network_info()
            
            assert result['source'] == 'rest'
            assert result['id'] == sample_network_info['id']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_get_network_info_not_authenticated(self, auth_manager):
        """Test get_network_info when not authenticated."""
        with patch.object(auth_manager, 'is_authenticated', return_value=False):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.get_network_info()
            
            assert "Not authenticated" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    @pytest.mark.network
    def test_get_network_info_both_apis_fail(self, auth_manager):
        """Test get_network_info with both APIs failing."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            # Mock SOAP API failure
            auth_manager._core_auth.get_soap_client.side_effect = Exception("SOAP error")
            
            # Mock REST API failure
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_session.get.return_value = mock_response
            auth_manager._core_auth.get_rest_session.return_value = mock_session
            
            with pytest.raises(NetworkError) as exc_info:
                auth_manager.get_network_info()
            
            assert "Failed to get network info from both APIs" in str(exc_info.value)


class TestAuthManagerScopeValidation:
    """Test AuthManager scope validation functionality."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_validate_scopes_with_valid_scopes(self, auth_manager, mock_oauth_credentials):
        """Test validate_scopes with valid scopes."""
        mock_oauth_credentials.scopes = [
            'https://www.googleapis.com/auth/dfp',
            'https://www.googleapis.com/auth/admanager'
        ]
        auth_manager._credentials = mock_oauth_credentials
        
        result = auth_manager.validate_scopes()
        
        assert result is auth_manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_validate_scopes_with_missing_scopes(self, auth_manager, mock_oauth_credentials):
        """Test validate_scopes with missing scopes."""
        mock_oauth_credentials.scopes = ['https://www.googleapis.com/auth/dfp']
        auth_manager._credentials = mock_oauth_credentials
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.validate_scopes()
        
        assert "Missing required scopes" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_validate_scopes_with_custom_scopes(self, auth_manager, mock_oauth_credentials):
        """Test validate_scopes with custom required scopes."""
        mock_oauth_credentials.scopes = ['https://www.googleapis.com/auth/dfp']
        auth_manager._credentials = mock_oauth_credentials
        
        custom_scopes = ['https://www.googleapis.com/auth/dfp']
        result = auth_manager.validate_scopes(custom_scopes)
        
        assert result is auth_manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_validate_scopes_no_credentials(self, auth_manager):
        """Test validate_scopes with no credentials."""
        auth_manager._credentials = None
        auth_manager._core_auth.get_oauth2_credentials.return_value = None
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.validate_scopes()
        
        assert "No credentials available for scope validation" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_validate_scopes_no_scope_info(self, auth_manager, mock_oauth_credentials):
        """Test validate_scopes when credentials have no scope information."""
        # Remove scopes attribute
        del mock_oauth_credentials.scopes
        auth_manager._credentials = mock_oauth_credentials
        
        result = auth_manager.validate_scopes()
        
        # Should succeed with warning
        assert result is auth_manager


class TestAuthManagerUtilities:
    """Test AuthManager utility methods."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_schedule_refresh(self, auth_manager):
        """Test schedule_refresh method (placeholder implementation)."""
        callback = Mock()
        
        result = auth_manager.schedule_refresh(callback, minutes_before_expiry=10)
        
        assert result is auth_manager
        # Currently just logs, so no actual scheduling
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_repr_authenticated(self, auth_manager):
        """Test __repr__ method when authenticated."""
        with patch.object(auth_manager, 'is_authenticated', return_value=True):
            repr_str = repr(auth_manager)
            
            assert "AuthManager(authenticated)" in repr_str
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_repr_not_authenticated(self, auth_manager):
        """Test __repr__ method when not authenticated."""
        with patch.object(auth_manager, 'is_authenticated', return_value=False):
            repr_str = repr(auth_manager)
            
            assert "AuthManager(not authenticated)" in repr_str


class TestAuthManagerErrorHandling:
    """Test AuthManager error handling scenarios."""
    
    @pytest.fixture
    def auth_manager(self, mock_config):
        """Create an AuthManager instance."""
        mock_core_auth = Mock()
        return AuthManager(mock_config, mock_core_auth)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_check_status_unexpected_error(self, auth_manager):
        """Test check_status with unexpected error."""
        with patch('src.sdk.auth.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("Unexpected error")
            
            result = auth_manager.check_status()
            
            # Should handle error gracefully
            assert result is auth_manager
            assert auth_manager._status is not None
            assert auth_manager._status['authenticated'] is False
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_refresh_credentials_error(self, auth_manager, mock_oauth_credentials):
        """Test refresh_if_needed with error during refresh."""
        mock_oauth_credentials.expired = True
        mock_oauth_credentials.refresh.side_effect = Exception("Refresh error")
        auth_manager._credentials = mock_oauth_credentials
        auth_manager._core_auth._get_request.return_value = Mock()
        
        with pytest.raises(AuthError) as exc_info:
            auth_manager.refresh_if_needed()
        
        assert "Failed to refresh credentials" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_login_flow_error(self, auth_manager):
        """Test login flow with error during setup."""
        with patch('src.sdk.auth.Flow', side_effect=Exception("Flow error")):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.login()
            
            assert "Login flow failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_connection_test_unexpected_error(self, auth_manager):
        """Test test_connection with unexpected error."""
        with patch.object(auth_manager, 'is_authenticated', side_effect=Exception("Unexpected error")):
            
            with pytest.raises(NetworkError) as exc_info:
                auth_manager.test_connection()
            
            assert "Connection test failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    @pytest.mark.auth
    def test_scope_validation_error(self, auth_manager):
        """Test validate_scopes with unexpected error."""
        with patch.object(auth_manager, 'check_status', side_effect=Exception("Check error")):
            
            with pytest.raises(AuthError) as exc_info:
                auth_manager.validate_scopes()
            
            assert "Scope validation failed" in str(exc_info.value)