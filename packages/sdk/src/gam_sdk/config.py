"""
Configuration management for the GAM SDK with fluent interface.

Provides chainable methods for configuration operations including
reading, writing, validation, and environment management.
"""

import os
import yaml
import logging
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
from copy import deepcopy

from gam_api.config import Config, get_config, reset_config
from gam_api.exceptions import ConfigurationError
from .exceptions import ConfigError, ValidationError

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Fluent configuration manager for GAM SDK.
    
    Provides chainable methods for configuration operations:
    - Reading and writing configuration values
    - Validation and testing
    - Environment management
    - File operations
    
    Usage:
        config = (client
            .config()
            .set('gam.network_code', '12345678')
            .set('logging.level', 'DEBUG')
            .validate()
            .save())
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize configuration manager.
        
        Args:
            config: Optional existing configuration to work with
        """
        self._config = config or get_config()
        self._changes = {}  # Track changes for batch operations
        self._config_path = None
        self._validation_results = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gam.network_code')
            default: Default value if key not found
            
        Returns:
            Configuration value
            
        Example:
            network_code = config.get('gam.network_code')
            timeout = config.get('api.timeout', 30)
        """
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> 'ConfigManager':
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gam.network_code')
            value: Value to set
            
        Returns:
            Self for chaining
            
        Example:
            config = (manager
                .set('gam.network_code', '12345678')
                .set('api.timeout', 60))
        """
        # Store change for later application
        self._changes[key] = value
        
        # Also update current config for immediate use
        try:
            self._apply_change(key, value)
        except Exception as e:
            logger.warning(f"Could not immediately apply config change {key}={value}: {e}")
        
        return self
    
    def _apply_change(self, key: str, value: Any) -> None:
        """Apply a configuration change to the current config object."""
        keys = key.split('.')
        
        # Navigate to the parent of the target key
        current = self._config
        for k in keys[:-1]:
            if not hasattr(current, k):
                # Create intermediate objects as needed
                setattr(current, k, type('ConfigSection', (), {})())
            current = getattr(current, k)
        
        # Set the final value
        setattr(current, keys[-1], value)
    
    def update(self, config_dict: Dict[str, Any]) -> 'ConfigManager':
        """
        Update multiple configuration values.
        
        Args:
            config_dict: Dictionary of key-value pairs to update
            
        Returns:
            Self for chaining
            
        Example:
            config = manager.update({
                'gam.network_code': '12345678',
                'api.timeout': 60,
                'logging.level': 'DEBUG'
            })
        """
        for key, value in config_dict.items():
            self.set(key, value)
        
        return self
    
    def load_from_file(self, file_path: Union[str, Path]) -> 'ConfigManager':
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Self for chaining
            
        Raises:
            ConfigError: If file cannot be loaded
        """
        try:
            file_path = Path(file_path)
            self._config_path = file_path
            
            if not file_path.exists():
                raise ConfigError(f"Configuration file not found: {file_path}")
            
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    import json
                    config_data = json.load(f)
                else:
                    raise ConfigError(f"Unsupported config file format: {file_path.suffix}")
            
            # Update config with loaded data
            for key, value in self._flatten_dict(config_data).items():
                self.set(key, value)
            
            logger.info(f"Configuration loaded from: {file_path}")
            return self
            
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {file_path}: {e}") from e
    
    def save_to_file(self, file_path: Optional[Union[str, Path]] = None, format: str = 'yaml') -> 'ConfigManager':
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save file (uses loaded path if not specified)
            format: File format ('yaml', 'json')
            
        Returns:
            Self for chaining
            
        Raises:
            ConfigError: If file cannot be saved
        """
        try:
            if file_path:
                save_path = Path(file_path)
            elif self._config_path:
                save_path = self._config_path
            else:
                raise ConfigError("No file path specified for saving")
            
            # Create directory if needed
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary
            config_dict = self._config_to_dict()
            
            # Apply pending changes
            for key, value in self._changes.items():
                self._set_nested_dict(config_dict, key.split('.'), value)
            
            # Save to file
            with open(save_path, 'w') as f:
                if format.lower() == 'yaml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                elif format.lower() == 'json':
                    import json
                    json.dump(config_dict, f, indent=2)
                else:
                    raise ConfigError(f"Unsupported format: {format}")
            
            logger.info(f"Configuration saved to: {save_path}")
            self._changes.clear()  # Clear pending changes
            return self
            
        except Exception as e:
            raise ConfigError(f"Failed to save configuration: {e}") from e
    
    def validate(self) -> 'ConfigManager':
        """
        Validate current configuration.
        
        Returns:
            Self for chaining
            
        Raises:
            ConfigError: If validation fails
        """
        try:
            self._validation_results = {}
            
            # Check required fields
            required_fields = {
                'gam.network_code': 'GAM network code is required',
                'gam.oauth2.client_id': 'OAuth2 client ID is required',
                'gam.oauth2.client_secret': 'OAuth2 client secret is required'
            }
            
            for field, message in required_fields.items():
                value = self.get(field)
                if not value:
                    self._validation_results[field] = f"❌ {message}"
                else:
                    self._validation_results[field] = "✅ Valid"
            
            # Validate network code format
            network_code = self.get('gam.network_code')
            if network_code:
                if not str(network_code).isdigit():
                    self._validation_results['gam.network_code'] = "❌ Network code must be numeric"
                elif len(str(network_code)) < 8:
                    self._validation_results['gam.network_code'] = "❌ Network code too short"
            
            # Validate OAuth2 client ID format
            client_id = self.get('gam.oauth2.client_id')
            if client_id and not str(client_id).endswith('.googleusercontent.com'):
                self._validation_results['gam.oauth2.client_id'] = "⚠️ Client ID format may be incorrect"
            
            # Check for any validation errors
            errors = [msg for msg in self._validation_results.values() if msg.startswith('❌')]
            if errors:
                raise ConfigError(f"Configuration validation failed: {len(errors)} errors found")
            
            logger.info("Configuration validation passed")
            return self
            
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}") from e
    
    def test_connection(self) -> 'ConfigManager':
        """
        Test connection to GAM API with current configuration.
        
        Returns:
            Self for chaining
            
        Raises:
            ConfigError: If connection test fails
        """
        try:
            from gam_api.auth import AuthManager
            
            # Create auth manager with current config
            auth_manager = AuthManager(self._config)
            
            # Test authentication
            credentials = auth_manager.get_oauth2_credentials()
            if not credentials or credentials.expired:
                raise ConfigError("Authentication failed - invalid or expired credentials")
            
            # Test API connection
            try:
                soap_client = auth_manager.get_soap_client()
                network_service = soap_client.GetService('NetworkService')
                current_network = network_service.getCurrentNetwork()
                
                logger.info(f"Connection test successful - connected to {current_network.get('displayName', 'GAM')}")
                
            except Exception as e:
                # Try REST API as fallback
                rest_session = auth_manager.get_rest_session()
                network_code = self.get('gam.network_code')
                url = f"https://admanager.googleapis.com/v1/networks/{network_code}"
                response = rest_session.get(url)
                
                if response.status_code == 200:
                    logger.info("Connection test successful via REST API")
                else:
                    raise ConfigError(f"API connection failed: HTTP {response.status_code}")
            
            return self
            
        except Exception as e:
            raise ConfigError(f"Connection test failed: {e}") from e
    
    def reset(self) -> 'ConfigManager':
        """
        Reset to default configuration.
        
        Returns:
            Self for chaining
        """
        reset_config()
        self._config = get_config()
        self._changes.clear()
        logger.info("Configuration reset to defaults")
        return self
    
    def show(self, hide_secrets: bool = True) -> Dict[str, Any]:
        """
        Get current configuration as dictionary.
        
        Args:
            hide_secrets: Whether to hide sensitive values
            
        Returns:
            Configuration dictionary
        """
        config_dict = self._config_to_dict()
        
        # Apply pending changes
        for key, value in self._changes.items():
            self._set_nested_dict(config_dict, key.split('.'), value)
        
        if hide_secrets:
            # Hide sensitive fields
            sensitive_fields = [
                'gam.oauth2.client_secret',
                'gam.oauth2.refresh_token'
            ]
            
            for field in sensitive_fields:
                keys = field.split('.')
                self._hide_nested_value(config_dict, keys)
        
        return config_dict
    
    def get_validation_results(self) -> Optional[Dict[str, str]]:
        """
        Get results from last validation.
        
        Returns:
            Validation results dictionary or None if not validated
        """
        return self._validation_results
    
    def has_pending_changes(self) -> bool:
        """
        Check if there are unsaved changes.
        
        Returns:
            True if there are pending changes
        """
        return bool(self._changes)
    
    def get_pending_changes(self) -> Dict[str, Any]:
        """
        Get dictionary of pending changes.
        
        Returns:
            Pending changes dictionary
        """
        return deepcopy(self._changes)
    
    def discard_changes(self) -> 'ConfigManager':
        """
        Discard pending changes.
        
        Returns:
            Self for chaining
        """
        self._changes.clear()
        logger.info("Pending configuration changes discarded")
        return self
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary using dot notation."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config object to dictionary."""
        try:
            # Try to convert config object to dict
            if hasattr(self._config, '__dict__'):
                return self._convert_attrs_to_dict(self._config)
            else:
                return {}
        except Exception:
            return {}
    
    def _convert_attrs_to_dict(self, obj) -> Dict[str, Any]:
        """Recursively convert object attributes to dictionary."""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if hasattr(value, '__dict__'):
                        result[key] = self._convert_attrs_to_dict(value)
                    else:
                        result[key] = value
            return result
        else:
            return obj
    
    def _set_nested_dict(self, d: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set value in nested dictionary using key path."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    
    def _hide_nested_value(self, d: Dict[str, Any], keys: List[str]) -> None:
        """Hide sensitive value in nested dictionary."""
        current = d
        for key in keys[:-1]:
            if key in current and isinstance(current[key], dict):
                current = current[key]
            else:
                return  # Path doesn't exist
        
        if keys[-1] in current and current[keys[-1]]:
            current[keys[-1]] = '***hidden***'
    
    def __repr__(self) -> str:
        """String representation."""
        pending = f", pending_changes={len(self._changes)}" if self._changes else ""
        return f"ConfigManager(network_code='{self.get('gam.network_code')}'{pending})"