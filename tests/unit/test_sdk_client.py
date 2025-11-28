"""
Unit tests for the GAM SDK client.

Tests the main GAMClient class functionality including initialization,
authentication, report access, configuration management, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from gam_sdk.client import GAMClient, create_client
from gam_sdk.exceptions import SDKError, ConfigError, AuthError
from gam_sdk.reports import ReportBuilder
from gam_sdk.config import ConfigManager
from gam_sdk.auth import AuthManager as SDKAuthManager


class TestGAMClientInitialization:
    """Test GAMClient initialization scenarios."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_basic_initialization(self, mock_config):
        """Test basic client initialization with default settings."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient()
            
            assert client is not None
            mock_get_config.assert_called_once()
            mock_auth_manager.assert_called_once_with(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_with_config_path(self, mock_config):
        """Test client initialization with custom config path."""
        config_path = "/path/to/config.yaml"
        
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient(config_path=config_path)
            
            mock_get_config.assert_called_once_with(config_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_with_network_code_override(self, mock_config):
        """Test client initialization with network code override."""
        network_code = "987654321"
        
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            # This should work when network code override is implemented
            client = GAMClient(network_code=network_code)
            
            assert client is not None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_without_auto_auth(self, mock_config):
        """Test client initialization without auto-authentication."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient(auto_authenticate=False)
            
            assert client is not None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_config_error(self):
        """Test client initialization with configuration error."""
        with patch('src.sdk.client.get_config') as mock_get_config:
            from gam_api.exceptions import ConfigurationError
            mock_get_config.side_effect = ConfigurationError("Config not found")
            
            with pytest.raises(ConfigError) as exc_info:
                GAMClient()
            
            assert "Failed to load configuration" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_auth_error(self, mock_config):
        """Test client initialization with authentication error."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            from gam_api.exceptions import AuthenticationError
            mock_get_config.return_value = mock_config
            mock_auth_manager.side_effect = AuthenticationError("Auth failed")
            
            with pytest.raises(AuthError) as exc_info:
                GAMClient(auto_authenticate=True)
            
            assert "Auto-authentication failed" in str(exc_info.value)


class TestGAMClientProperties:
    """Test GAMClient properties and basic methods."""
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a test client."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            return GAMClient(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_network_code_property(self, client, mock_config):
        """Test network_code property."""
        client._config = mock_config
        assert client.network_code == mock_config.auth.network_code
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_network_code_property_no_config(self, client):
        """Test network_code property when config is None."""
        client._config = None
        assert client.network_code is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_is_authenticated_property_true(self, client):
        """Test is_authenticated property when authenticated."""
        with patch.object(client, '_ensure_authenticated'):
            assert client.is_authenticated is True
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_is_authenticated_property_false(self, client):
        """Test is_authenticated property when not authenticated."""
        with patch.object(client, '_ensure_authenticated', side_effect=AuthError("Not authenticated")):
            assert client.is_authenticated is False


class TestGAMClientReports:
    """Test GAMClient report functionality."""
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a test client."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            return GAMClient(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_reports_method(self, client):
        """Test reports() method returns ReportBuilder."""
        with patch('src.sdk.client.ReportBuilder') as mock_builder:
            mock_instance = Mock(spec=ReportBuilder)
            mock_builder.return_value = mock_instance
            
            result = client.reports()
            
            assert result == mock_instance
            mock_builder.assert_called_once_with(client._config, client._auth_manager)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_reports_method_with_auto_auth(self, client):
        """Test reports() method with auto-authentication."""
        client._auto_authenticate = True
        
        with patch.object(client, '_ensure_authenticated') as mock_ensure_auth, \
             patch('src.sdk.client.ReportBuilder') as mock_builder:
            
            mock_instance = Mock(spec=ReportBuilder)
            mock_builder.return_value = mock_instance
            
            result = client.reports()
            
            mock_ensure_auth.assert_called_once()
            assert result == mock_instance
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_quick_report_method(self, client, mock_report_result):
        """Test quick_report() method."""
        with patch.object(client, 'reports') as mock_reports:
            # Setup mock chain
            mock_builder = Mock()
            mock_builder.quick.return_value = mock_builder
            mock_builder.days_back.return_value = mock_builder
            mock_builder.execute.return_value = mock_report_result
            mock_reports.return_value = mock_builder
            
            result = client.quick_report('delivery', days_back=7)
            
            assert result == mock_report_result
            mock_builder.quick.assert_called_once_with('delivery')
            mock_builder.days_back.assert_called_once_with(7)
            mock_builder.execute.assert_called_once()


class TestGAMClientConfiguration:
    """Test GAMClient configuration management."""
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a test client."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            return GAMClient(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_config_method_first_call(self, client):
        """Test config() method on first call."""
        with patch('src.sdk.client.ConfigManager') as mock_config_manager:
            mock_instance = Mock(spec=ConfigManager)
            mock_config_manager.return_value = mock_instance
            
            result = client.config()
            
            assert result == mock_instance
            assert client._config_manager == mock_instance
            mock_config_manager.assert_called_once_with(client._config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_config_method_cached(self, client):
        """Test config() method returns cached instance."""
        mock_instance = Mock(spec=ConfigManager)
        client._config_manager = mock_instance
        
        result = client.config()
        
        assert result == mock_instance


class TestGAMClientAuthentication:
    """Test GAMClient authentication functionality."""
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a test client."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            return GAMClient(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_auth_method_first_call(self, client):
        """Test auth() method on first call."""
        with patch('src.sdk.client.SDKAuthManager') as mock_auth_manager:
            mock_instance = Mock(spec=SDKAuthManager)
            mock_auth_manager.return_value = mock_instance
            
            result = client.auth()
            
            assert result == mock_instance
            assert client._sdk_auth_manager == mock_instance
            mock_auth_manager.assert_called_once_with(client._config, client._auth_manager)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_auth_method_cached(self, client):
        """Test auth() method returns cached instance."""
        mock_instance = Mock(spec=SDKAuthManager)
        client._sdk_auth_manager = mock_instance
        
        result = client.auth()
        
        assert result == mock_instance
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_ensure_authenticated_already_authenticated(self, client):
        """Test _ensure_authenticated when already authenticated."""
        client._authenticated = True
        
        # Should return immediately without doing anything
        client._ensure_authenticated()
        
        assert client._authenticated is True
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_ensure_authenticated_valid_credentials(self, client, mock_oauth_credentials):
        """Test _ensure_authenticated with valid credentials."""
        client._authenticated = False
        
        with patch.object(client._auth_manager, 'get_oauth2_credentials') as mock_get_creds:
            mock_get_creds.return_value = mock_oauth_credentials
            
            client._ensure_authenticated()
            
            assert client._authenticated is True
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_ensure_authenticated_expired_credentials(self, client, mock_oauth_credentials):
        """Test _ensure_authenticated with expired credentials that can be refreshed."""
        client._authenticated = False
        mock_oauth_credentials.expired = True
        
        with patch.object(client._auth_manager, 'get_oauth2_credentials') as mock_get_creds, \
             patch.object(client._auth_manager, '_get_request') as mock_get_request:
            
            mock_get_creds.return_value = mock_oauth_credentials
            mock_get_request.return_value = Mock()
            
            client._ensure_authenticated()
            
            mock_oauth_credentials.refresh.assert_called_once()
            assert client._authenticated is True
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_ensure_authenticated_no_credentials(self, client):
        """Test _ensure_authenticated with no credentials."""
        client._authenticated = False
        
        with patch.object(client._auth_manager, 'get_oauth2_credentials') as mock_get_creds:
            mock_get_creds.return_value = None
            
            with pytest.raises(AuthError) as exc_info:
                client._ensure_authenticated()
            
            assert "No valid authentication credentials found" in str(exc_info.value)


class TestGAMClientConnectionTesting:
    """Test GAMClient connection testing functionality."""
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a test client."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            return GAMClient(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_success(self, client, sample_network_info):
        """Test successful connection test."""
        with patch.object(client, '_ensure_authenticated'), \
             patch.object(client._auth_manager, 'get_soap_client') as mock_soap, \
             patch.object(client._auth_manager, 'get_rest_session') as mock_rest:
            
            # Mock SOAP API success
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = sample_network_info
            mock_soap_client = Mock()
            mock_soap_client.GetService.return_value = mock_network_service
            mock_soap.return_value = mock_soap_client
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_rest.return_value = mock_session
            
            result = client.test_connection()
            
            assert result['authenticated'] is True
            assert result['overall_status'] == 'healthy'
            assert result['soap_api']['status'] == 'connected'
            assert result['rest_api']['status'] == 'connected'
            assert result['network_info'] == {
                'id': sample_network_info.get('id'),
                'networkCode': sample_network_info.get('networkCode'),
                'displayName': sample_network_info.get('displayName'),
                'timeZone': sample_network_info.get('timeZone'),
                'currencyCode': sample_network_info.get('currencyCode')
            }
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_soap_failure_rest_success(self, client):
        """Test connection test with SOAP failure but REST success."""
        with patch.object(client, '_ensure_authenticated'), \
             patch.object(client._auth_manager, 'get_soap_client') as mock_soap, \
             patch.object(client._auth_manager, 'get_rest_session') as mock_rest:
            
            # Mock SOAP API failure
            mock_soap.side_effect = Exception("SOAP error")
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_rest.return_value = mock_session
            
            result = client.test_connection()
            
            assert result['authenticated'] is True
            assert result['overall_status'] == 'healthy'
            assert result['soap_api']['status'] == 'error'
            assert result['rest_api']['status'] == 'connected'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_both_apis_fail(self, client):
        """Test connection test with both APIs failing."""
        with patch.object(client, '_ensure_authenticated'), \
             patch.object(client._auth_manager, 'get_soap_client') as mock_soap, \
             patch.object(client._auth_manager, 'get_rest_session') as mock_rest:
            
            # Mock SOAP API failure
            mock_soap.side_effect = Exception("SOAP error")
            
            # Mock REST API failure
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_session.get.return_value = mock_response
            mock_rest.return_value = mock_session
            
            result = client.test_connection()
            
            assert result['authenticated'] is True
            assert result['overall_status'] == 'unhealthy'
            assert result['soap_api']['status'] == 'error'
            assert result['rest_api']['status'] == 'error'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_auth_error(self, client):
        """Test connection test with authentication error."""
        with patch.object(client, '_ensure_authenticated', side_effect=AuthError("Not authenticated")):
            
            result = client.test_connection()
            
            assert result['authenticated'] is False
            assert result['overall_status'] == 'unauthenticated'


class TestGAMClientContextManager:
    """Test GAMClient context manager functionality."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_context_manager_enter_exit(self, mock_config):
        """Test context manager enter and exit."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient(auto_authenticate=False)
            
            # Test __enter__
            result = client.__enter__()
            assert result is client
            
            # Test __exit__
            client.__exit__(None, None, None)
            # Should not raise any exceptions


class TestGAMClientUtilities:
    """Test GAMClient utility functions."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_create_client_function(self, mock_config):
        """Test create_client utility function."""
        with patch('src.sdk.client.GAMClient') as mock_client_class:
            mock_instance = Mock()
            mock_client_class.return_value = mock_instance
            
            result = create_client(auto_authenticate=False)
            
            assert result == mock_instance
            mock_client_class.assert_called_once_with(auto_authenticate=False)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_client_repr(self, mock_config):
        """Test client string representation."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient(auto_authenticate=False)
            client._config = mock_config
            
            with patch.object(client, 'is_authenticated', return_value=True):
                result = repr(client)
                
                assert "GAMClient" in result
                assert mock_config.auth.network_code in result
                assert "authenticated=True" in result


class TestGAMClientErrorHandling:
    """Test GAMClient error handling scenarios."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_generic_initialization_error(self):
        """Test generic error during initialization."""
        with patch('src.sdk.client.get_config', side_effect=Exception("Generic error")):
            
            with pytest.raises(SDKError) as exc_info:
                GAMClient()
            
            assert "Client initialization failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_authentication_error_handling(self, mock_config):
        """Test authentication error handling in ensure_authenticated."""
        with patch('src.sdk.client.get_config') as mock_get_config, \
             patch('src.sdk.client.AuthManager') as mock_auth_manager:
            
            mock_get_config.return_value = mock_config
            mock_auth_manager.return_value = Mock()
            
            client = GAMClient(auto_authenticate=False)
            client._authenticated = False
            
            with patch.object(client._auth_manager, 'get_oauth2_credentials', side_effect=Exception("Auth error")):
                
                with pytest.raises(AuthError) as exc_info:
                    client._ensure_authenticated()
                
                assert "Authentication verification failed" in str(exc_info.value)