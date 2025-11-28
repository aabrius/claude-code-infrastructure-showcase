"""
Unified configuration loading utilities for all GAM API applications.

This module provides a consistent configuration interface that bridges between:
1. The new gam_api package configuration system
2. Application-specific configuration needs (Pydantic, environment variables, etc.)
3. Legacy configuration formats for backward compatibility

Usage Examples:
    # Load configuration for specific application
    config = UnifiedConfigLoader.load_for_application("mcp_server")
    
    # Load from environment variables only
    env_config = UnifiedConfigLoader.get_environment_config()
    
    # Validate configuration for specific application
    is_valid = UnifiedConfigLoader.validate_config(config, "report_builder")
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import asdict
from enum import Enum

# Import from gam_api package for core configuration
try:
    from gam_api import load_config as gam_load_config
    from gam_api.config.loader import Config as GAMConfig, AuthConfig, APIConfig, CacheConfig, LoggingConfig, DefaultsConfig
    from gam_api.exceptions import ConfigurationError
    HAS_GAM_API = True
except ImportError:
    # Fallback for environments without gam_api package
    HAS_GAM_API = False
    class ConfigurationError(Exception):
        pass

logger = logging.getLogger(__name__)


class ApplicationType(Enum):
    """Supported application types."""
    MCP_SERVER = "mcp_server"
    REPORT_BUILDER = "report_builder"
    CLI = "cli"
    API_SERVER = "api_server"
    SDK = "sdk"


class UnifiedConfigLoader:
    """
    Unified configuration loader for all GAM API applications.
    
    This class provides methods to load configuration that works across
    all applications while respecting each application's specific needs.
    """
    
    @staticmethod
    def load_for_application(
        app_name: str, 
        config_path: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load configuration optimized for a specific application.
        
        Args:
            app_name: Application name (mcp_server, report_builder, cli, api_server, sdk)
            config_path: Optional path to configuration file
            environment: Environment override (development, staging, production)
            
        Returns:
            Configuration dictionary optimized for the application
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or validated
        """
        logger.info(f"Loading configuration for application: {app_name}")
        
        # Validate application name
        try:
            app_type = ApplicationType(app_name)
        except ValueError:
            valid_apps = [app.value for app in ApplicationType]
            raise ConfigurationError(f"Unknown application '{app_name}'. Valid applications: {valid_apps}")
        
        # Load base configuration
        if HAS_GAM_API:
            try:
                gam_config = gam_load_config(config_path)
                base_config = gam_config.to_dict()
                logger.info("Loaded configuration using gam_api package")
            except Exception as e:
                logger.warning(f"Failed to load with gam_api, falling back to manual loading: {e}")
                base_config = UnifiedConfigLoader._load_manual_config(config_path)
        else:
            logger.info("gam_api package not available, using manual configuration loading")
            base_config = UnifiedConfigLoader._load_manual_config(config_path)
        
        # Load application-specific configuration
        app_config = UnifiedConfigLoader._load_app_specific_config(config_path)
        
        # Merge configurations
        unified_config = UnifiedConfigLoader._merge_configs(base_config, app_config)
        
        # Apply environment overrides
        if environment:
            unified_config = UnifiedConfigLoader._apply_environment_overrides(unified_config, environment)
        
        # Extract application-specific configuration
        app_specific_config = UnifiedConfigLoader._extract_app_config(unified_config, app_type)
        
        # Validate configuration
        UnifiedConfigLoader.validate_config(app_specific_config, app_name)
        
        logger.info(f"Successfully loaded configuration for {app_name}")
        return app_specific_config
    
    @staticmethod
    def get_environment_config() -> Dict[str, Any]:
        """
        Load configuration from environment variables only.
        
        Returns:
            Configuration dictionary built from environment variables
        """
        logger.info("Loading configuration from environment variables")
        
        # GAM configuration from environment
        gam_config = {
            'network_code': os.getenv('GAM_NETWORK_CODE'),
            'application_name': os.getenv('GAM_APPLICATION_NAME', 'GAM API Suite'),
            'timeout_seconds': int(os.getenv('GAM_TIMEOUT_SECONDS', '300'))
        }
        
        # Authentication configuration
        auth_config = {
            'type': os.getenv('GAM_AUTH_TYPE', 'oauth2'),
            'oauth2': {
                'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
                'refresh_token': os.getenv('GOOGLE_OAUTH_REFRESH_TOKEN')
            }
        }
        
        # Service account configuration (if provided)
        service_account_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH')
        if service_account_path:
            auth_config['service_account'] = {
                'path': service_account_path,
                'impersonate_user': os.getenv('GOOGLE_IMPERSONATE_USER')
            }
        
        # API configuration
        api_config = {
            'preference': os.getenv('GAM_API_PREFERENCE'),  # None, "soap", "rest"
            'enable_fallback': os.getenv('GAM_ENABLE_FALLBACK', 'true').lower() == 'true',
            'timeout_seconds': int(os.getenv('GAM_API_TIMEOUT', '30')),
            'max_retries': int(os.getenv('GAM_MAX_RETRIES', '3')),
            'retry_delay': float(os.getenv('GAM_RETRY_DELAY', '1.0'))
        }
        
        # Application-specific configurations
        mcp_config = {
            'enabled': os.getenv('MCP_ENABLED', 'true').lower() == 'true',
            'transport': os.getenv('MCP_TRANSPORT', 'stdio'),
            'auth_enabled': os.getenv('MCP_AUTH_ENABLED', 'false').lower() == 'true',
            'host': os.getenv('MCP_HOST', '0.0.0.0'),
            'port': int(os.getenv('MCP_PORT', '8080'))
        }
        
        report_builder_config = {
            'enabled': os.getenv('REPORT_BUILDER_ENABLED', 'true').lower() == 'true',
            'frontend_url': os.getenv('REPORT_BUILDER_FRONTEND_URL', 'http://localhost:5173'),
            'backend': {
                'host': os.getenv('REPORT_BUILDER_HOST', '0.0.0.0'),
                'port': int(os.getenv('REPORT_BUILDER_PORT', '8000')),
                'debug': os.getenv('REPORT_BUILDER_DEBUG', 'false').lower() == 'true'
            }
        }
        
        api_server_config = {
            'enabled': os.getenv('API_SERVER_ENABLED', 'true').lower() == 'true',
            'host': os.getenv('API_SERVER_HOST', '0.0.0.0'),
            'port': int(os.getenv('API_SERVER_PORT', '8001')),
            'debug': os.getenv('API_SERVER_DEBUG', 'false').lower() == 'true',
            'api_key': os.getenv('GAM_API_KEY')
        }
        
        # Cache configuration
        cache_config = {
            'enabled': os.getenv('GAM_CACHE_ENABLED', 'true').lower() == 'true',
            'backend': os.getenv('GAM_CACHE_BACKEND', 'file'),
            'ttl': int(os.getenv('GAM_CACHE_TTL', '3600')),
            'directory': os.getenv('GAM_CACHE_DIRECTORY', 'cache'),
            'max_size_mb': int(os.getenv('GAM_CACHE_MAX_SIZE_MB', '100'))
        }
        
        # Logging configuration
        logging_config = {
            'level': os.getenv('GAM_LOG_LEVEL', 'INFO'),
            'format': os.getenv('GAM_LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file': os.getenv('GAM_LOG_FILE'),
            'directory': os.getenv('GAM_LOG_DIRECTORY', 'logs'),
            'include_console': os.getenv('GAM_LOG_CONSOLE', 'true').lower() == 'true'
        }
        
        # Combine all configurations
        env_config = {
            'gam': gam_config,
            'auth': auth_config,
            'api': api_config,
            'mcp': mcp_config,
            'report_builder': report_builder_config,
            'api_server': api_server_config,
            'performance': {
                'cache': cache_config
            },
            'logging': logging_config
        }
        
        # Remove None values
        env_config = UnifiedConfigLoader._clean_none_values(env_config)
        
        return env_config
    
    @staticmethod
    def validate_config(config: Dict[str, Any], app_name: str) -> List[str]:
        """
        Validate configuration for specific application requirements.
        
        Args:
            config: Configuration dictionary to validate
            app_name: Application name for validation rules
            
        Returns:
            List of validation errors (empty if valid)
            
        Raises:
            ConfigurationError: If validation fails with critical errors
        """
        errors = []
        warnings = []
        
        try:
            app_type = ApplicationType(app_name)
        except ValueError:
            return [f"Unknown application type: {app_name}"]
        
        # Core GAM configuration validation
        gam_config = config.get('gam', {})
        if not gam_config.get('network_code'):
            errors.append("gam.network_code is required")
        
        # Authentication validation
        auth_config = config.get('auth', {})
        auth_type = auth_config.get('type', 'oauth2')
        
        if auth_type == 'oauth2':
            oauth2_config = auth_config.get('oauth2', {})
            required_oauth2_fields = ['client_id', 'client_secret', 'refresh_token']
            for field in required_oauth2_fields:
                if not oauth2_config.get(field):
                    errors.append(f"auth.oauth2.{field} is required for OAuth2 authentication")
        
        elif auth_type == 'service_account':
            service_account_config = auth_config.get('service_account', {})
            if not service_account_config.get('path'):
                errors.append("auth.service_account.path is required for service account authentication")
        
        # Application-specific validation
        if app_type == ApplicationType.MCP_SERVER:
            mcp_config = config.get('mcp', {})
            if mcp_config.get('transport') == 'http' and not mcp_config.get('port'):
                errors.append("mcp.port is required for HTTP transport")
        
        elif app_type == ApplicationType.REPORT_BUILDER:
            rb_config = config.get('report_builder', {})
            if not rb_config.get('frontend_url'):
                warnings.append("report_builder.frontend_url not specified, using default")
            
            backend_config = rb_config.get('backend', {})
            if not backend_config.get('port'):
                warnings.append("report_builder.backend.port not specified, using default")
        
        elif app_type == ApplicationType.API_SERVER:
            api_config = config.get('api_server', {})
            if not api_config.get('api_key'):
                errors.append("api_server.api_key is required for API authentication")
        
        # Performance configuration validation
        perf_config = config.get('performance', {})
        cache_config = perf_config.get('cache', {})
        if cache_config.get('enabled') and cache_config.get('ttl', 0) <= 0:
            errors.append("performance.cache.ttl must be positive when cache is enabled")
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"Configuration validation warning: {warning}")
        
        # Raise exception if critical errors found
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_message)
            raise ConfigurationError(error_message)
        
        return errors
    
    @staticmethod
    def create_application_config_template(app_name: str, output_path: str):
        """
        Create a configuration template file for a specific application.
        
        Args:
            app_name: Application name
            output_path: Path where to save the template
        """
        try:
            app_type = ApplicationType(app_name)
        except ValueError:
            raise ConfigurationError(f"Unknown application type: {app_name}")
        
        # Load base template
        base_template_path = Path(__file__).parent / "master_config.yaml.example"
        
        if base_template_path.exists():
            with open(base_template_path, 'r') as f:
                template_content = f.read()
        else:
            logger.warning("Base template not found, creating minimal template")
            template_content = UnifiedConfigLoader._create_minimal_template(app_type)
        
        # Write application-specific template
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(f"# Configuration template for {app_name}\n")
            f.write(f"# Generated from master template\n\n")
            f.write(template_content)
        
        logger.info(f"Created configuration template for {app_name} at {output_path}")
    
    # Private helper methods
    
    @staticmethod
    def _load_manual_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration manually when gam_api package is not available."""
        config_files = []
        
        if config_path:
            config_files = [config_path]
        else:
            # Search for configuration files in order of preference
            possible_paths = [
                "config/master_config.yaml",
                "config/agent_config.yaml",
                "agent_config.yaml",
                "googleads.yaml",
                os.path.expanduser("~/.config/gam-api/config.yaml")
            ]
            config_files = [path for path in possible_paths if os.path.exists(path)]
        
        if not config_files:
            logger.info("No configuration files found, using environment variables only")
            return UnifiedConfigLoader.get_environment_config()
        
        # Load the first found configuration file
        config_file = config_files[0]
        logger.info(f"Loading configuration from: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            return config_data
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_file}: {e}")
    
    @staticmethod
    def _load_app_specific_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load additional application-specific configuration files."""
        app_configs = {}
        
        # Look for application-specific configuration files
        app_config_paths = [
            "config/mcp_server.yaml",
            "config/report_builder.yaml",
            "config/api_server.yaml",
            "config/cli.yaml"
        ]
        
        for config_file in app_config_paths:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        app_data = yaml.safe_load(f) or {}
                    app_name = Path(config_file).stem
                    app_configs[app_name] = app_data
                    logger.debug(f"Loaded application-specific config: {config_file}")
                except Exception as e:
                    logger.warning(f"Failed to load application config {config_file}: {e}")
        
        return app_configs
    
    @staticmethod
    def _merge_configs(base_config: Dict[str, Any], app_configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge base configuration with application-specific configurations."""
        merged = base_config.copy()
        
        # Merge each application-specific configuration
        for app_name, app_config in app_configs.items():
            if app_name in merged:
                # Deep merge
                merged[app_name] = UnifiedConfigLoader._deep_merge(merged[app_name], app_config)
            else:
                merged[app_name] = app_config
        
        return merged
    
    @staticmethod
    def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = UnifiedConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def _apply_environment_overrides(config: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides."""
        env_overrides = config.get('environments', {}).get(environment, {})
        
        if env_overrides:
            logger.info(f"Applying {environment} environment overrides")
            config = UnifiedConfigLoader._deep_merge(config, env_overrides)
        
        return config
    
    @staticmethod
    def _extract_app_config(unified_config: Dict[str, Any], app_type: ApplicationType) -> Dict[str, Any]:
        """Extract application-specific configuration from unified configuration."""
        # Always include core configurations
        app_config = {
            'gam': unified_config.get('gam', {}),
            'auth': unified_config.get('auth', {}),
            'api': unified_config.get('api', {}),
            'performance': unified_config.get('performance', {}),
            'logging': unified_config.get('logging', {}),
            'reports': unified_config.get('reports', {})
        }
        
        # Add application-specific configuration
        if app_type == ApplicationType.MCP_SERVER:
            app_config['mcp'] = unified_config.get('mcp', {})
        elif app_type == ApplicationType.REPORT_BUILDER:
            app_config['report_builder'] = unified_config.get('report_builder', {})
        elif app_type == ApplicationType.API_SERVER:
            app_config['api_server'] = unified_config.get('api_server', {})
        elif app_type == ApplicationType.CLI:
            app_config['cli'] = unified_config.get('cli', {})
        elif app_type == ApplicationType.SDK:
            app_config['sdk'] = unified_config.get('sdk', {})
        
        # Add features and security configurations
        app_config['features'] = unified_config.get('features', {})
        app_config['security'] = unified_config.get('security', {})
        
        return app_config
    
    @staticmethod
    def _clean_none_values(config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values from configuration dictionary."""
        cleaned = {}
        
        for key, value in config.items():
            if value is not None:
                if isinstance(value, dict):
                    cleaned_value = UnifiedConfigLoader._clean_none_values(value)
                    if cleaned_value:  # Only add if not empty
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
        
        return cleaned
    
    @staticmethod
    def _create_minimal_template(app_type: ApplicationType) -> str:
        """Create a minimal configuration template for the application type."""
        minimal_template = f"""# Minimal configuration template for {app_type.value}

gam:
  network_code: "${{GAM_NETWORK_CODE}}"
  application_name: "GAM API {app_type.value.replace('_', ' ').title()}"
  timeout_seconds: 300

auth:
  type: "oauth2"
  oauth2:
    client_id: "${{GOOGLE_OAUTH_CLIENT_ID}}"
    client_secret: "${{GOOGLE_OAUTH_CLIENT_SECRET}}"
    refresh_token: "${{GOOGLE_OAUTH_REFRESH_TOKEN}}"

api:
  preference: null
  enable_fallback: true
  timeout_seconds: 30

logging:
  level: "INFO"
  include_console: true

performance:
  cache:
    enabled: true
    ttl: 3600
"""
        
        # Add application-specific sections
        if app_type == ApplicationType.MCP_SERVER:
            minimal_template += """
mcp:
  enabled: true
  transport: "stdio"
  auth_enabled: false
"""
        elif app_type == ApplicationType.REPORT_BUILDER:
            minimal_template += """
report_builder:
  enabled: true
  frontend_url: "http://localhost:5173"
  backend:
    host: "0.0.0.0"
    port: 8000
"""
        elif app_type == ApplicationType.API_SERVER:
            minimal_template += """
api_server:
  enabled: true
  host: "0.0.0.0"
  port: 8001
  api_key: "${{GAM_API_KEY}}"
"""
        
        return minimal_template


# Convenience functions for backward compatibility and ease of use

def load_config_for_app(app_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration for a specific application.
    
    Args:
        app_name: Application name (mcp_server, report_builder, cli, api_server, sdk)
        config_path: Optional path to configuration file
        
    Returns:
        Configuration dictionary optimized for the application
    """
    return UnifiedConfigLoader.load_for_application(app_name, config_path)


def validate_app_config(config: Dict[str, Any], app_name: str) -> bool:
    """
    Convenience function to validate configuration for an application.
    
    Args:
        config: Configuration dictionary to validate
        app_name: Application name
        
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: If validation fails
    """
    errors = UnifiedConfigLoader.validate_config(config, app_name)
    return len(errors) == 0


def create_config_template(app_name: str, output_path: str):
    """
    Convenience function to create a configuration template.
    
    Args:
        app_name: Application name
        output_path: Path where to save the template
    """
    UnifiedConfigLoader.create_application_config_template(app_name, output_path)


def get_env_config() -> Dict[str, Any]:
    """
    Convenience function to get configuration from environment variables.
    
    Returns:
        Configuration dictionary from environment variables
    """
    return UnifiedConfigLoader.get_environment_config()