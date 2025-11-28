"""
Unit tests for authentication management.
"""

import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock

from gam_api.auth import AuthManager, get_auth_manager
from gam_api.config import Config, AuthConfig
from gam_api.exceptions import AuthenticationError, ConfigurationError


class TestAuthManager:
    """Test AuthManager functionality."""
    
    def test_init_with_config(self, mock_config):
        """Test AuthManager initialization with config."""
        with patch('src.core.auth.get_config', return_value=mock_config):
            with patch('src.core.auth.load_config', return_value=mock_config):
                auth_manager = AuthManager()
                
                assert auth_manager.config == mock_config
                assert auth_manager.network_code == "123456789"
    
    def test_validate_config_success(self, mock_config):
        """Test successful config validation."""
        with patch('src.core.auth.get_config', return_value=mock_config):
            with patch('src.core.auth.load_config', return_value=mock_config):
                auth_manager = AuthManager()
        
        # Should not raise any exceptions
        auth_manager.validate_config()
    
    def test_validate_config_missing_network_code(self, mock_config):
        """Test config validation with missing network code."""
        mock_config.auth.network_code = None
        with patch('src.core.auth.get_config', return_value=mock_config):
            with patch('src.core.auth.load_config', return_value=mock_config):
                auth_manager = AuthManager()
                
                with pytest.raises(ConfigurationError, match="Network code is required"):
                    auth_manager.validate_config()
    
    def test_validate_config_missing_client_id(self, mock_config):
        """Test config validation with missing client ID."""
        mock_config.auth.client_id = None
        with patch('src.core.auth.get_config', return_value=mock_config):
            with patch('src.core.auth.load_config', return_value=mock_config):
                auth_manager = AuthManager()
                
                with pytest.raises(ConfigurationError, match="Client ID is required"):
                    auth_manager.validate_config()
    
    def test_get_credentials(self, mock_config):
        """Test getting OAuth2 credentials."""
        auth_manager = AuthManager(mock_config)
        credentials = auth_manager.get_credentials()
        
        expected = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'refresh_token': 'test_refresh_token'
        }
        
        assert credentials == expected
    
    @patch('src.core.auth.ad_manager.AdManagerClient')
    def test_get_soap_client_success(self, mock_client_class, mock_config):
        """Test successful SOAP client creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        auth_manager = AuthManager(mock_config)
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.yaml'
            
            with patch('yaml.dump') as mock_dump:
                with patch('os.unlink') as mock_unlink:
                    client = auth_manager.get_soap_client()
                    
                    assert client == mock_client
                    mock_client_class.assert_called_once()
    
    @patch('src.core.auth.ad_manager.AdManagerClient')
    def test_get_soap_client_failure(self, mock_client_class, mock_config):
        """Test SOAP client creation failure."""
        mock_client_class.side_effect = Exception("SOAP client error")
        
        auth_manager = AuthManager(mock_config)
        
        with pytest.raises(AuthenticationError, match="Failed to create SOAP client"):
            auth_manager.get_soap_client()
    
    def test_create_legacy_yaml_format(self, mock_config):
        """Test creation of legacy YAML format."""
        auth_manager = AuthManager(mock_config)
        legacy_data = auth_manager._create_legacy_yaml_data()
        
        expected = {
            'ad_manager': {
                'network_code': '123456789',
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret',
                'refresh_token': 'test_refresh_token'
            }
        }
        
        assert legacy_data == expected


class TestAuthManagerIntegration:
    """Test AuthManager integration scenarios."""
    
    def test_end_to_end_auth_flow(self, mock_config):
        """Test complete authentication flow."""
        auth_manager = AuthManager(mock_config)
        
        # Validate config
        auth_manager.validate_config()
        
        # Get credentials
        credentials = auth_manager.get_credentials()
        assert 'client_id' in credentials
        assert 'client_secret' in credentials
        assert 'refresh_token' in credentials
        
        # Create legacy YAML data
        legacy_data = auth_manager._create_legacy_yaml_data()
        assert 'ad_manager' in legacy_data
        assert legacy_data['ad_manager']['network_code'] == '123456789'
    
    @patch('src.core.auth.get_config')
    def test_get_auth_manager_singleton(self, mock_get_config, mock_config):
        """Test that get_auth_manager returns singleton."""
        mock_get_config.return_value = mock_config
        
        auth1 = get_auth_manager()
        auth2 = get_auth_manager()
        
        # Should be the same instance (singleton)
        assert auth1 is auth2
    
    def test_refresh_token_validation(self, mock_config):
        """Test refresh token validation."""
        # Valid refresh token
        auth_manager = AuthManager(mock_config)
        auth_manager.validate_config()  # Should not raise
        
        # Invalid refresh token
        mock_config.auth.refresh_token = ""
        with pytest.raises(ConfigurationError, match="Refresh token is required"):
            auth_manager.validate_config()
    
    def test_network_code_validation(self, mock_config):
        """Test network code validation."""
        # Valid network code
        auth_manager = AuthManager(mock_config)
        auth_manager.validate_config()  # Should not raise
        
        # Invalid network code (not numeric)
        mock_config.auth.network_code = "invalid"
        auth_manager = AuthManager(mock_config)
        # Should still work - network code can be alphanumeric
        auth_manager.validate_config()
        
        # Empty network code
        mock_config.auth.network_code = ""
        with pytest.raises(ConfigurationError, match="Network code is required"):
            auth_manager.validate_config()


class TestAuthManagerErrorHandling:
    """Test error handling in AuthManager."""
    
    def test_invalid_config_type(self):
        """Test AuthManager with invalid config type."""
        with pytest.raises(TypeError):
            AuthManager("invalid_config")
    
    def test_missing_auth_section(self):
        """Test config missing auth section."""
        config = Mock()
        config.auth = None
        
        with pytest.raises(AttributeError):
            AuthManager(config)
    
    @patch('src.core.auth.ad_manager.AdManagerClient')
    def test_soap_client_network_error(self, mock_client_class, mock_config):
        """Test SOAP client creation with network error."""
        mock_client_class.side_effect = ConnectionError("Network error")
        
        auth_manager = AuthManager(mock_config)
        
        with pytest.raises(AuthenticationError, match="Failed to create SOAP client"):
            auth_manager.get_soap_client()
    
    def test_credentials_with_missing_fields(self, mock_config):
        """Test getting credentials with missing fields."""
        mock_config.auth.client_secret = None
        
        auth_manager = AuthManager(mock_config)
        
        with pytest.raises(ConfigurationError):
            auth_manager.validate_config()