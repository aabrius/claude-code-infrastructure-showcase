"""
Configuration management for Google Ad Manager API with unified client support.

This module provides configuration loading and management for both legacy
and modern configuration formats, with extended support for unified client
settings including API selection preferences and fallback configurations.
"""

import os
import logging
import yaml
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .exceptions import ConfigurationError


logger = logging.getLogger(__name__)


@dataclass
class AuthConfig:
    """Authentication configuration."""
    network_code: str
    client_id: str
    client_secret: str
    refresh_token: str
    service_account_path: Optional[str] = None
    impersonate_user: Optional[str] = None


@dataclass
class APIConfig:
    """API configuration."""
    prefer_rest: bool = True
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    backend: str = "file"
    ttl: int = 3600
    directory: str = "cache"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: Optional[str] = None
    directory: str = "logs"
    include_console: bool = True


@dataclass
class DefaultsConfig:
    """Default settings for operations."""
    days_back: int = 30
    format: str = "json"
    max_rows_preview: int = 10
    max_pages: int = 5
    timeout: int = 300


@dataclass
class UnifiedClientConfig:
    """Configuration for unified client behavior and API selection."""
    api_preference: Optional[str] = None  # 'soap', 'rest', or None for auto
    enable_fallback: bool = True
    enable_performance_tracking: bool = True
    performance_threshold: float = 0.8
    complexity_threshold: int = 10
    
    # Circuit breaker settings
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    
    # Retry settings
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    retry_strategy: str = 'exponential'  # 'linear', 'exponential', 'fibonacci'
    
    # Operation-specific settings
    operation_preferences: Optional[Dict[str, str]] = None
    operation_timeouts: Optional[Dict[str, int]] = None
    operation_retry_configs: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class Config:
    """Complete configuration object."""
    auth: AuthConfig
    api: APIConfig
    cache: CacheConfig
    logging: LoggingConfig
    defaults: DefaultsConfig
    unified: UnifiedClientConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format for adapters."""
        return {
            'auth': {
                'network_code': self.auth.network_code,
                'client_id': self.auth.client_id,
                'client_secret': self.auth.client_secret,
                'refresh_token': self.auth.refresh_token,
                'service_account_path': self.auth.service_account_path,
                'impersonate_user': self.auth.impersonate_user
            },
            'api': {
                'prefer_rest': self.api.prefer_rest,
                'timeout': self.api.timeout,
                'max_retries': self.api.max_retries,
                'retry_delay': self.api.retry_delay
            },
            'cache': {
                'enabled': self.cache.enabled,
                'backend': self.cache.backend,
                'ttl': self.cache.ttl,
                'directory': self.cache.directory
            },
            'logging': {
                'level': self.logging.level,
                'file': self.logging.file,
                'directory': self.logging.directory,
                'include_console': self.logging.include_console
            },
            'defaults': {
                'days_back': self.defaults.days_back,
                'format': self.defaults.format,
                'max_rows_preview': self.defaults.max_rows_preview,
                'max_pages': self.defaults.max_pages,
                'timeout': self.defaults.timeout
            },
            'unified': {
                'api_preference': self.unified.api_preference,
                'enable_fallback': self.unified.enable_fallback,
                'enable_performance_tracking': self.unified.enable_performance_tracking,
                'performance_threshold': self.unified.performance_threshold,
                'complexity_threshold': self.unified.complexity_threshold,
                'circuit_breaker_threshold': self.unified.circuit_breaker_threshold,
                'circuit_breaker_timeout': self.unified.circuit_breaker_timeout,
                'max_retries': self.unified.max_retries,
                'base_delay': self.unified.base_delay,
                'max_delay': self.unified.max_delay,
                'backoff_multiplier': self.unified.backoff_multiplier,
                'retry_strategy': self.unified.retry_strategy,
                'operation_preferences': self.unified.operation_preferences,
                'operation_timeouts': self.unified.operation_timeouts,
                'operation_retry_configs': self.unified.operation_retry_configs
            }
        }


class ConfigLoader:
    """Configuration loader that supports multiple formats."""
    
    def __init__(self):
        """Initialize configuration loader."""
        self._config: Optional[Config] = None
    
    def load_config(self, config_path: Optional[str] = None) -> Config:
        """
        Load configuration from available sources.
        
        Priority order:
        1. Explicit config_path parameter
        2. agent_config.yaml (new format)
        3. googleads.yaml (legacy format)
        4. Environment variables
        
        Args:
            config_path: Optional explicit path to config file
            
        Returns:
            Loaded configuration object
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        if self._config is not None:
            return self._config
        
        # Try explicit path first
        if config_path and os.path.exists(config_path):
            logger.info(f"Loading configuration from explicit path: {config_path}")
            self._config = self._load_from_file(config_path)
            return self._config
        
        # Try new format
        agent_config_path = self._find_agent_config()
        if agent_config_path:
            logger.info(f"Loading configuration from agent config: {agent_config_path}")
            self._config = self._load_agent_config(agent_config_path)
            return self._config
        
        # Try legacy format
        legacy_config_path = self._find_legacy_config()
        if legacy_config_path:
            logger.info(f"Loading configuration from legacy config: {legacy_config_path}")
            self._config = self._load_legacy_config(legacy_config_path)
            return self._config
        
        # Try environment variables
        try:
            logger.info("Loading configuration from environment variables")
            self._config = self._load_from_env()
            return self._config
        except ConfigurationError:
            pass
        
        raise ConfigurationError(
            "No valid configuration found. Please provide one of:\n"
            "1. config/agent_config.yaml (new format)\n"
            "2. googleads.yaml (legacy format)\n"
            "3. Environment variables (GAM_NETWORK_CODE, GAM_CLIENT_ID, etc.)"
        )
    
    def _find_agent_config(self) -> Optional[str]:
        """Find agent configuration file."""
        possible_paths = [
            "config/agent_config.yaml",
            "agent_config.yaml",
            os.path.expanduser("~/.config/gam-api/agent_config.yaml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_legacy_config(self) -> Optional[str]:
        """Find legacy configuration file."""
        possible_paths = [
            "googleads.yaml",
            os.path.expanduser("~/.googleads.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "..", "googleads.yaml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _load_from_file(self, config_path: str) -> Config:
        """Load configuration from any file, detecting format."""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Detect format by checking structure
            if 'ad_manager' in data:
                return self._parse_legacy_format(data)
            elif 'auth' in data:
                return self._parse_agent_format(data)
            else:
                raise ConfigurationError(f"Unknown configuration format in {config_path}")
                
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    
    def _load_agent_config(self, config_path: str) -> Config:
        """Load new agent configuration format."""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            return self._parse_agent_format(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load agent config: {e}")
    
    def _load_legacy_config(self, config_path: str) -> Config:
        """Load legacy googleads.yaml format."""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            return self._parse_legacy_format(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load legacy config: {e}")
    
    def _load_from_env(self) -> Config:
        """Load configuration from environment variables."""
        required_vars = [
            'GAM_NETWORK_CODE',
            'GAM_CLIENT_ID', 
            'GAM_CLIENT_SECRET',
            'GAM_REFRESH_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        auth = AuthConfig(
            network_code=os.getenv('GAM_NETWORK_CODE'),
            client_id=os.getenv('GAM_CLIENT_ID'),
            client_secret=os.getenv('GAM_CLIENT_SECRET'),
            refresh_token=os.getenv('GAM_REFRESH_TOKEN'),
            service_account_path=os.getenv('GAM_SERVICE_ACCOUNT_PATH'),
            impersonate_user=os.getenv('GAM_IMPERSONATE_USER')
        )
        
        api = APIConfig(
            prefer_rest=os.getenv('GAM_PREFER_REST', 'true').lower() == 'true',
            timeout=int(os.getenv('GAM_TIMEOUT', '30')),
            max_retries=int(os.getenv('GAM_MAX_RETRIES', '3')),
            retry_delay=float(os.getenv('GAM_RETRY_DELAY', '1.0'))
        )
        
        cache = CacheConfig(
            enabled=os.getenv('GAM_CACHE_ENABLED', 'true').lower() == 'true',
            backend=os.getenv('GAM_CACHE_BACKEND', 'file'),
            ttl=int(os.getenv('GAM_CACHE_TTL', '3600')),
            directory=os.getenv('GAM_CACHE_DIRECTORY', 'cache')
        )
        
        logging_config = LoggingConfig(
            level=os.getenv('GAM_LOG_LEVEL', 'INFO'),
            file=os.getenv('GAM_LOG_FILE'),
            directory=os.getenv('GAM_LOG_DIRECTORY', 'logs'),
            include_console=os.getenv('GAM_LOG_CONSOLE', 'true').lower() == 'true'
        )
        
        defaults = DefaultsConfig(
            days_back=int(os.getenv('GAM_DEFAULT_DAYS_BACK', '30')),
            format=os.getenv('GAM_DEFAULT_FORMAT', 'json'),
            max_rows_preview=int(os.getenv('GAM_DEFAULT_MAX_ROWS_PREVIEW', '10')),
            max_pages=int(os.getenv('GAM_DEFAULT_MAX_PAGES', '5')),
            timeout=int(os.getenv('GAM_DEFAULT_TIMEOUT', '300'))
        )
        
        unified = UnifiedClientConfig(
            api_preference=os.getenv('GAM_UNIFIED_API_PREFERENCE'),
            enable_fallback=os.getenv('GAM_UNIFIED_ENABLE_FALLBACK', 'true').lower() == 'true',
            enable_performance_tracking=os.getenv('GAM_UNIFIED_PERFORMANCE_TRACKING', 'true').lower() == 'true',
            performance_threshold=float(os.getenv('GAM_UNIFIED_PERFORMANCE_THRESHOLD', '0.8')),
            complexity_threshold=int(os.getenv('GAM_UNIFIED_COMPLEXITY_THRESHOLD', '10')),
            circuit_breaker_threshold=int(os.getenv('GAM_UNIFIED_CIRCUIT_BREAKER_THRESHOLD', '5')),
            circuit_breaker_timeout=float(os.getenv('GAM_UNIFIED_CIRCUIT_BREAKER_TIMEOUT', '60.0')),
            max_retries=int(os.getenv('GAM_UNIFIED_MAX_RETRIES', '3')),
            base_delay=float(os.getenv('GAM_UNIFIED_BASE_DELAY', '1.0')),
            max_delay=float(os.getenv('GAM_UNIFIED_MAX_DELAY', '60.0')),
            backoff_multiplier=float(os.getenv('GAM_UNIFIED_BACKOFF_MULTIPLIER', '2.0')),
            retry_strategy=os.getenv('GAM_UNIFIED_RETRY_STRATEGY', 'exponential')
        )
        
        return Config(
            auth=auth,
            api=api,
            cache=cache,
            logging=logging_config,
            defaults=defaults,
            unified=unified
        )
    
    def _parse_agent_format(self, data: Dict[str, Any]) -> Config:
        """Parse new agent configuration format."""
        try:
            auth_data = data.get('auth', {})
            oauth2_data = auth_data.get('oauth2', {})
            
            auth = AuthConfig(
                network_code=auth_data.get('network_code'),
                client_id=oauth2_data.get('client_id'),
                client_secret=oauth2_data.get('client_secret'),
                refresh_token=oauth2_data.get('refresh_token'),
                service_account_path=auth_data.get('service_account', {}).get('path'),
                impersonate_user=auth_data.get('service_account', {}).get('impersonate_user')
            )
            
            api_data = data.get('api', {})
            api = APIConfig(
                prefer_rest=api_data.get('prefer_rest', True),
                timeout=api_data.get('timeout', 30),
                max_retries=api_data.get('max_retries', 3),
                retry_delay=api_data.get('retry_delay', 1.0)
            )
            
            cache_data = data.get('cache', {})
            cache = CacheConfig(
                enabled=cache_data.get('enabled', True),
                backend=cache_data.get('backend', 'file'),
                ttl=cache_data.get('ttl', 3600),
                directory=cache_data.get('directory', 'cache')
            )
            
            logging_data = data.get('logging', {})
            logging_config = LoggingConfig(
                level=logging_data.get('level', 'INFO'),
                file=logging_data.get('file'),
                directory=logging_data.get('directory', 'logs'),
                include_console=logging_data.get('include_console', True)
            )
            
            defaults_data = data.get('defaults', {})
            defaults = DefaultsConfig(
                days_back=defaults_data.get('days_back', 30),
                format=defaults_data.get('format', 'json'),
                max_rows_preview=defaults_data.get('max_rows_preview', 10),
                max_pages=defaults_data.get('max_pages', 5),
                timeout=defaults_data.get('timeout', 300)
            )
            
            unified_data = data.get('unified', {})
            unified = UnifiedClientConfig(
                api_preference=unified_data.get('api_preference'),
                enable_fallback=unified_data.get('enable_fallback', True),
                enable_performance_tracking=unified_data.get('enable_performance_tracking', True),
                performance_threshold=unified_data.get('performance_threshold', 0.8),
                complexity_threshold=unified_data.get('complexity_threshold', 10),
                circuit_breaker_threshold=unified_data.get('circuit_breaker_threshold', 5),
                circuit_breaker_timeout=unified_data.get('circuit_breaker_timeout', 60.0),
                max_retries=unified_data.get('max_retries', 3),
                base_delay=unified_data.get('base_delay', 1.0),
                max_delay=unified_data.get('max_delay', 60.0),
                backoff_multiplier=unified_data.get('backoff_multiplier', 2.0),
                retry_strategy=unified_data.get('retry_strategy', 'exponential'),
                operation_preferences=unified_data.get('operation_preferences'),
                operation_timeouts=unified_data.get('operation_timeouts'),
                operation_retry_configs=unified_data.get('operation_retry_configs')
            )
            
            return Config(
                auth=auth,
                api=api,
                cache=cache,
                logging=logging_config,
                defaults=defaults,
                unified=unified
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to parse agent configuration: {e}")
    
    def _parse_legacy_format(self, data: Dict[str, Any]) -> Config:
        """Parse legacy googleads.yaml format."""
        try:
            ad_manager_data = data.get('ad_manager', {})
            
            auth = AuthConfig(
                network_code=ad_manager_data.get('network_code'),
                client_id=ad_manager_data.get('client_id'),
                client_secret=ad_manager_data.get('client_secret'),
                refresh_token=ad_manager_data.get('refresh_token')
            )
            
            # Use defaults for other settings in legacy format
            api = APIConfig()
            cache = CacheConfig()
            logging_config = LoggingConfig()
            defaults = DefaultsConfig()
            unified = UnifiedClientConfig()  # Use all defaults
            
            return Config(
                auth=auth,
                api=api,
                cache=cache,
                logging=logging_config,
                defaults=defaults,
                unified=unified
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to parse legacy configuration: {e}")


# Global configuration loader instance
_config_loader: Optional[ConfigLoader] = None


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration using global loader instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Loaded configuration object
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.load_config(config_path)


def get_config() -> Optional[Config]:
    """Get current configuration if loaded."""
    global _config_loader
    return _config_loader._config if _config_loader else None


def reset_config():
    """Reset configuration loader to force reload."""
    global _config_loader
    _config_loader = None


# Re-export for backward compatibility
__all__ = [
    "AuthConfig",
    "APIConfig", 
    "CacheConfig",
    "LoggingConfig",
    "DefaultsConfig",
    "UnifiedClientConfig",
    "Config",
    "ConfigLoader",
    "load_config",
    "get_config",
    "reset_config",
]