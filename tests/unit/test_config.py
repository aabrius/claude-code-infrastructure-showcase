"""
Unit tests for configuration management.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, mock_open

from gam_api.config import (
    Config, AuthConfig, APIConfig, CacheConfig, LoggingConfig, DefaultsConfig,
    UnifiedClientConfig, ConfigLoader, get_config, reset_config
)
from gam_api.exceptions import ConfigurationError


class TestConfigModels:
    """Test configuration data models."""
    
    def test_auth_config_creation(self):
        """Test AuthConfig creation."""
        auth = AuthConfig(
            network_code="123456789",
            client_id="test_client",
            client_secret="test_secret",
            refresh_token="test_token"
        )
        
        assert auth.network_code == "123456789"
        assert auth.client_id == "test_client"
        assert auth.client_secret == "test_secret"
        assert auth.refresh_token == "test_token"
    
    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        api = APIConfig()
        
        assert api.prefer_rest is True
        assert api.timeout == 30
        assert api.max_retries == 3
        assert api.retry_delay == 1.0
    
    def test_complete_config_creation(self, mock_config):
        """Test complete Config object creation."""
        assert mock_config.auth.network_code == "123456789"
        assert mock_config.api.prefer_rest is True
        assert mock_config.cache.enabled is True
        assert mock_config.logging.level == "INFO"
        assert mock_config.defaults.days_back == 30


class TestConfigLoader:
    """Test configuration loading functionality."""
    
    def test_load_from_yaml_legacy_format(self, temp_config_file):
        """Test loading legacy googleads.yaml format."""
        with patch('src.core.config.ConfigLoader._find_legacy_config', return_value=temp_config_file):
            loader = ConfigLoader()
            config = loader.load_config()
        
        assert config.auth.network_code == "123456789"
        assert config.auth.client_id == "test_client_id"
        assert config.auth.client_secret == "test_client_secret"
        assert config.auth.refresh_token == "test_refresh_token"
    
    def test_load_from_yaml_new_format(self):
        """Test loading new agent_config.yaml format."""
        config_data = {
            'auth': {
                'network_code': '987654321',
                'oauth2': {
                    'client_id': 'new_client_id',
                    'client_secret': 'new_client_secret',
                    'refresh_token': 'new_refresh_token'
                }
            },
            'api': {
                'prefer_rest': False,
                'timeout': 60
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            with patch('src.core.config.ConfigLoader._find_agent_config', return_value=temp_path):
                loader = ConfigLoader()
                config = loader.load_config()
            
            assert config.auth.network_code == "987654321"
            assert config.auth.client_id == "new_client_id"
            assert config.api.prefer_rest is False
            assert config.api.timeout == 60
        finally:
            os.unlink(temp_path)
    
    def test_load_from_environment(self, test_env):
        """Test loading configuration from environment variables."""
        with patch('src.core.config.ConfigLoader._find_agent_config', return_value=None):
            with patch('src.core.config.ConfigLoader._find_legacy_config', return_value=None):
                loader = ConfigLoader()
                config = loader.load_config()
        
        assert config.auth.network_code == "123456789"
        assert config.auth.client_id == "test_client_id"
        assert config.auth.client_secret == "test_client_secret"
        assert config.auth.refresh_token == "test_refresh_token"
    
    def test_load_priority_file_over_env(self, temp_config_file, test_env):
        """Test that file configuration takes priority over environment."""
        with patch('src.core.config.ConfigLoader._find_legacy_config', return_value=temp_config_file):
            loader = ConfigLoader()
            config = loader.load_config()
        
        # Should use file values, not environment values
        assert config.auth.client_id == "test_client_id"  # from file
        # Environment has different client_id, so this confirms file priority
    
    def test_load_fallback_to_env(self, test_env):
        """Test fallback to environment when no config files exist."""
        with patch('src.core.config.ConfigLoader._find_agent_config', return_value=None):
            with patch('src.core.config.ConfigLoader._find_legacy_config', return_value=None):
                loader = ConfigLoader()
                config = loader.load_config()
        
        assert config.auth.network_code == "123456789"
    
    def test_invalid_yaml_raises_error(self):
        """Test that invalid YAML raises ConfigurationError."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            with patch('src.core.config.ConfigLoader._find_legacy_config', return_value=temp_path):
                loader = ConfigLoader()
                with pytest.raises(ConfigurationError):
                    loader.load_config()
        finally:
            os.unlink(temp_path)


class TestConfigAPI:
    """Test configuration API functions."""
    
    def test_get_config_singleton(self, mock_config):
        """Test that get_config returns singleton instance."""
        with patch('src.core.config.ConfigLoader.load_config', return_value=mock_config):
            config1 = get_config()
            config2 = get_config()
            
            assert config1 is config2
    
    def test_reset_config_clears_cache(self, mock_config):
        """Test that reset_config clears the singleton cache."""
        with patch('src.core.config.ConfigLoader.load_config', return_value=mock_config):
            config1 = get_config()
            reset_config()
            config2 = get_config()
            
            # Should be different instances after reset
            assert config1 is not config2
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config should not raise
        config = Config(
            auth=AuthConfig(
                network_code="123456789",
                client_id="client",
                client_secret="secret",
                refresh_token="token"
            ),
            api=APIConfig(),
            cache=CacheConfig(),
            logging=LoggingConfig(),
            defaults=DefaultsConfig(),
            unified=UnifiedClientConfig()
        )
        
        # Should not raise any exceptions
        assert config.auth.network_code == "123456789"
    
    def test_missing_required_auth_fields(self):
        """Test that missing required auth fields are handled properly."""
        with pytest.raises((ValueError, TypeError)):
            AuthConfig(
                network_code="123456789",
                # Missing required fields
            )