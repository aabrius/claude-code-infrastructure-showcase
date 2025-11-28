"""
Unit tests for the GAM SDK configuration module.

Tests the ConfigManager class functionality including configuration
reading/writing, validation, file operations, and fluent interface.
"""

import pytest
import yaml
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from gam_sdk.config import ConfigManager
from gam_sdk.exceptions import ConfigError, ValidationError
from gam_api.exceptions import ConfigurationError


class TestConfigManagerInitialization:
    """Test ConfigManager initialization."""
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_with_config(self, mock_config):
        """Test initialization with provided config."""
        manager = ConfigManager(mock_config)
        
        assert manager._config == mock_config
        assert manager._changes == {}
        assert manager._config_path is None
        assert manager._validation_results is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_initialization_without_config(self):
        """Test initialization without provided config."""
        with patch('src.sdk.config.get_config') as mock_get_config:
            mock_config = Mock()
            mock_get_config.return_value = mock_config
            
            manager = ConfigManager()
            
            assert manager._config == mock_config
            mock_get_config.assert_called_once()


class TestConfigManagerGetSet:
    """Test ConfigManager get/set operations."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        return ConfigManager(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_existing_value(self, config_manager, mock_config):
        """Test getting existing configuration value."""
        # Mock the config structure
        mock_config.auth.network_code = "123456789"
        
        result = config_manager.get('auth.network_code')
        
        assert result == "123456789"
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_nonexistent_value_with_default(self, config_manager):
        """Test getting non-existent value with default."""
        result = config_manager.get('nonexistent.key', 'default_value')
        
        assert result == 'default_value'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_nonexistent_value_without_default(self, config_manager):
        """Test getting non-existent value without default."""
        result = config_manager.get('nonexistent.key')
        
        assert result is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_set_value(self, config_manager):
        """Test setting configuration value."""
        result = config_manager.set('test.key', 'test_value')
        
        # Should return self for chaining
        assert result is config_manager
        
        # Should be in pending changes
        assert config_manager._changes['test.key'] == 'test_value'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_set_multiple_values_chaining(self, config_manager):
        """Test setting multiple values with method chaining."""
        result = (config_manager
                  .set('key1', 'value1')
                  .set('key2', 'value2')
                  .set('key3', 'value3'))
        
        assert result is config_manager
        assert config_manager._changes['key1'] == 'value1'
        assert config_manager._changes['key2'] == 'value2'
        assert config_manager._changes['key3'] == 'value3'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_update_method(self, config_manager):
        """Test update method with dictionary."""
        config_dict = {
            'gam.network_code': '123456789',
            'api.timeout': 60,
            'logging.level': 'DEBUG'
        }
        
        result = config_manager.update(config_dict)
        
        assert result is config_manager
        assert config_manager._changes == config_dict


class TestConfigManagerFileOperations:
    """Test ConfigManager file operations."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        return ConfigManager(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_from_yaml_file(self, config_manager):
        """Test loading configuration from YAML file."""
        config_data = {
            'gam': {
                'network_code': '123456789',
                'oauth2': {
                    'client_id': 'test_client_id'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            result = config_manager.load_from_file(temp_path)
            
            assert result is config_manager
            assert config_manager._config_path == Path(temp_path)
            assert 'gam.network_code' in config_manager._changes
            assert 'gam.oauth2.client_id' in config_manager._changes
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_from_json_file(self, config_manager):
        """Test loading configuration from JSON file."""
        config_data = {
            'gam': {
                'network_code': '123456789'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            result = config_manager.load_from_file(temp_path)
            
            assert result is config_manager
            assert 'gam.network_code' in config_manager._changes
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_from_nonexistent_file(self, config_manager):
        """Test loading from non-existent file."""
        with pytest.raises(ConfigError) as exc_info:
            config_manager.load_from_file('/nonexistent/file.yaml')
        
        assert "Configuration file not found" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_from_unsupported_format(self, config_manager):
        """Test loading from unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some content")
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                config_manager.load_from_file(temp_path)
            
            assert "Unsupported config file format" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_save_to_yaml_file(self, config_manager):
        """Test saving configuration to YAML file."""
        config_manager.set('test.key', 'test_value')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            result = config_manager.save_to_file(temp_path, format='yaml')
            
            assert result is config_manager
            assert os.path.exists(temp_path)
            
            # Verify saved content
            with open(temp_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert 'test' in saved_data
            assert saved_data['test']['key'] == 'test_value'
            
            # Changes should be cleared
            assert config_manager._changes == {}
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_save_to_json_file(self, config_manager):
        """Test saving configuration to JSON file."""
        config_manager.set('test.key', 'test_value')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            result = config_manager.save_to_file(temp_path, format='json')
            
            assert result is config_manager
            assert os.path.exists(temp_path)
            
            # Verify saved content
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert 'test' in saved_data
            assert saved_data['test']['key'] == 'test_value'
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_save_without_path(self, config_manager):
        """Test saving without specifying path when no path loaded."""
        with pytest.raises(ConfigError) as exc_info:
            config_manager.save_to_file()
        
        assert "No file path specified for saving" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_save_unsupported_format(self, config_manager):
        """Test saving with unsupported format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                config_manager.save_to_file(temp_path, format='txt')
            
            assert "Unsupported format" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)


class TestConfigManagerValidation:
    """Test ConfigManager validation functionality."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        manager = ConfigManager(mock_config)
        # Set up mock for valid configuration
        mock_config.auth.network_code = "123456789"
        mock_config.auth.oauth2.client_id = "test_client_id.googleusercontent.com"
        mock_config.auth.oauth2.client_secret = "test_client_secret"
        return manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validate_valid_config(self, config_manager):
        """Test validation with valid configuration."""
        result = config_manager.validate()
        
        assert result is config_manager
        assert config_manager._validation_results is not None
        
        # All required fields should be valid
        for field, result_msg in config_manager._validation_results.items():
            if field in ['gam.network_code', 'gam.oauth2.client_id', 'gam.oauth2.client_secret']:
                assert result_msg.startswith('✅')
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validate_missing_network_code(self, config_manager):
        """Test validation with missing network code."""
        # Remove network code
        with patch.object(config_manager, 'get', side_effect=lambda key, default=None: None if key == 'gam.network_code' else 'value'):
            
            with pytest.raises(ConfigError) as exc_info:
                config_manager.validate()
            
            assert "Configuration validation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validate_invalid_network_code_format(self, config_manager):
        """Test validation with invalid network code format."""
        # Set invalid network code (non-numeric)
        with patch.object(config_manager, 'get') as mock_get:
            mock_get.side_effect = lambda key, default=None: {
                'gam.network_code': 'invalid_code',
                'gam.oauth2.client_id': 'test_client_id.googleusercontent.com',
                'gam.oauth2.client_secret': 'test_client_secret'
            }.get(key, default)
            
            with pytest.raises(ConfigError):
                config_manager.validate()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validate_short_network_code(self, config_manager):
        """Test validation with too short network code."""
        # Set short network code
        with patch.object(config_manager, 'get') as mock_get:
            mock_get.side_effect = lambda key, default=None: {
                'gam.network_code': '123',  # Too short
                'gam.oauth2.client_id': 'test_client_id.googleusercontent.com',
                'gam.oauth2.client_secret': 'test_client_secret'
            }.get(key, default)
            
            with pytest.raises(ConfigError):
                config_manager.validate()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validate_invalid_client_id_format(self, config_manager):
        """Test validation with invalid client ID format."""
        # Set invalid client ID (doesn't end with .googleusercontent.com)
        with patch.object(config_manager, 'get') as mock_get:
            mock_get.side_effect = lambda key, default=None: {
                'gam.network_code': '123456789',
                'gam.oauth2.client_id': 'invalid_client_id',
                'gam.oauth2.client_secret': 'test_client_secret'
            }.get(key, default)
            
            result = config_manager.validate()
            
            # Should pass validation but show warning
            assert result is config_manager
            assert '⚠️' in config_manager._validation_results['gam.oauth2.client_id']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_validation_results(self, config_manager):
        """Test getting validation results."""
        config_manager.validate()
        
        results = config_manager.get_validation_results()
        
        assert results is not None
        assert isinstance(results, dict)
        assert 'gam.network_code' in results


class TestConfigManagerConnectionTesting:
    """Test ConfigManager connection testing functionality."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        return ConfigManager(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_success(self, config_manager, sample_network_info):
        """Test successful connection test."""
        with patch('src.sdk.config.AuthManager') as mock_auth_manager_class:
            # Mock successful authentication and API calls
            mock_auth_manager = Mock()
            mock_auth_manager_class.return_value = mock_auth_manager
            
            mock_credentials = Mock()
            mock_credentials.expired = False
            mock_auth_manager.get_oauth2_credentials.return_value = mock_credentials
            
            # Mock SOAP API success
            mock_soap_client = Mock()
            mock_network_service = Mock()
            mock_network_service.getCurrentNetwork.return_value = sample_network_info
            mock_soap_client.GetService.return_value = mock_network_service
            mock_auth_manager.get_soap_client.return_value = mock_soap_client
            
            result = config_manager.test_connection()
            
            assert result is config_manager
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_auth_failure(self, config_manager):
        """Test connection test with authentication failure."""
        with patch('src.sdk.config.AuthManager') as mock_auth_manager_class:
            mock_auth_manager = Mock()
            mock_auth_manager_class.return_value = mock_auth_manager
            
            # Mock expired credentials
            mock_credentials = Mock()
            mock_credentials.expired = True
            mock_auth_manager.get_oauth2_credentials.return_value = mock_credentials
            
            with pytest.raises(ConfigError) as exc_info:
                config_manager.test_connection()
            
            assert "Authentication failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_test_connection_soap_failure_rest_success(self, config_manager):
        """Test connection test with SOAP failure but REST success."""
        with patch('src.sdk.config.AuthManager') as mock_auth_manager_class:
            mock_auth_manager = Mock()
            mock_auth_manager_class.return_value = mock_auth_manager
            
            # Mock valid credentials
            mock_credentials = Mock()
            mock_credentials.expired = False
            mock_auth_manager.get_oauth2_credentials.return_value = mock_credentials
            
            # Mock SOAP API failure
            mock_auth_manager.get_soap_client.side_effect = Exception("SOAP error")
            
            # Mock REST API success
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.get.return_value = mock_response
            mock_auth_manager.get_rest_session.return_value = mock_session
            
            # Mock config get for network code
            with patch.object(config_manager, 'get', return_value='123456789'):
                result = config_manager.test_connection()
                
                assert result is config_manager


class TestConfigManagerUtilities:
    """Test ConfigManager utility methods."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        return ConfigManager(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_reset_method(self, config_manager):
        """Test reset method."""
        # Add some changes
        config_manager.set('test.key', 'test_value')
        
        with patch('src.sdk.config.reset_config') as mock_reset, \
             patch('src.sdk.config.get_config') as mock_get_config:
            
            mock_new_config = Mock()
            mock_get_config.return_value = mock_new_config
            
            result = config_manager.reset()
            
            assert result is config_manager
            assert config_manager._config == mock_new_config
            assert config_manager._changes == {}
            mock_reset.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_show_method_with_secrets(self, config_manager):
        """Test show method with secrets hidden."""
        config_manager.set('gam.oauth2.client_secret', 'secret_value')
        config_manager.set('gam.oauth2.refresh_token', 'token_value')
        config_manager.set('public.setting', 'public_value')
        
        result = config_manager.show(hide_secrets=True)
        
        assert isinstance(result, dict)
        # Secrets should be hidden
        # Public settings should be visible
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_show_method_without_hiding_secrets(self, config_manager):
        """Test show method without hiding secrets."""
        config_manager.set('gam.oauth2.client_secret', 'secret_value')
        config_manager.set('public.setting', 'public_value')
        
        result = config_manager.show(hide_secrets=False)
        
        assert isinstance(result, dict)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_has_pending_changes(self, config_manager):
        """Test has_pending_changes method."""
        # Initially no changes
        assert not config_manager.has_pending_changes()
        
        # Add a change
        config_manager.set('test.key', 'test_value')
        assert config_manager.has_pending_changes()
        
        # Clear changes
        config_manager.discard_changes()
        assert not config_manager.has_pending_changes()
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_get_pending_changes(self, config_manager):
        """Test get_pending_changes method."""
        config_manager.set('key1', 'value1')
        config_manager.set('key2', 'value2')
        
        changes = config_manager.get_pending_changes()
        
        assert changes == {'key1': 'value1', 'key2': 'value2'}
        
        # Should return a copy, not the original
        changes['key3'] = 'value3'
        assert 'key3' not in config_manager._changes
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_discard_changes(self, config_manager):
        """Test discard_changes method."""
        config_manager.set('test.key', 'test_value')
        
        result = config_manager.discard_changes()
        
        assert result is config_manager
        assert config_manager._changes == {}
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_repr_method(self, config_manager):
        """Test __repr__ method."""
        with patch.object(config_manager, 'get', return_value='123456789'):
            # Without pending changes
            repr_str = repr(config_manager)
            assert "ConfigManager" in repr_str
            assert "123456789" in repr_str
            assert "pending_changes" not in repr_str
            
            # With pending changes
            config_manager.set('test.key', 'test_value')
            repr_str = repr(config_manager)
            assert "pending_changes=1" in repr_str


class TestConfigManagerErrorHandling:
    """Test ConfigManager error handling."""
    
    @pytest.fixture
    def config_manager(self, mock_config):
        """Create a ConfigManager instance."""
        return ConfigManager(mock_config)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_load_file_error(self, config_manager):
        """Test error handling during file loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigError) as exc_info:
                config_manager.load_from_file(temp_path)
            
            assert "Failed to load configuration" in str(exc_info.value)
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_save_file_error(self, config_manager):
        """Test error handling during file saving."""
        # Try to save to invalid path
        with pytest.raises(ConfigError) as exc_info:
            config_manager.save_to_file('/invalid/path/config.yaml')
        
        assert "Failed to save configuration" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_validation_error(self, config_manager):
        """Test error handling during validation."""
        with patch.object(config_manager, 'get', side_effect=Exception("Get error")):
            
            with pytest.raises(ConfigError) as exc_info:
                config_manager.validate()
            
            assert "Configuration validation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_connection_test_error(self, config_manager):
        """Test error handling during connection test."""
        with patch('src.sdk.config.AuthManager', side_effect=Exception("Auth manager error")):
            
            with pytest.raises(ConfigError) as exc_info:
                config_manager.test_connection()
            
            assert "Connection test failed" in str(exc_info.value)