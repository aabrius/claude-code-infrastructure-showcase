"""
Configuration validation for different GAM API application types.

This module provides validation logic specific to each application type,
ensuring that required configuration fields are present and valid.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ApplicationType(Enum):
    """Supported application types for validation."""
    MCP_SERVER = "mcp_server"
    REPORT_BUILDER = "report_builder"
    CLI = "cli"
    API_SERVER = "api_server" 
    SDK = "sdk"


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    ERROR = "error"      # Critical issues that prevent operation
    WARNING = "warning"  # Issues that may affect functionality
    INFO = "info"        # Informational messages


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    severity: ValidationSeverity
    field: str
    message: str
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        prefix = {
            ValidationSeverity.ERROR: "❌",
            ValidationSeverity.WARNING: "⚠️ ",
            ValidationSeverity.INFO: "ℹ️ "
        }[self.severity]
        
        result = f"{prefix} {self.field}: {self.message}"
        if self.suggestion:
            result += f" (Suggestion: {self.suggestion})"
        return result


class ConfigValidator:
    """
    Validates configurations for different application types.
    
    Provides comprehensive validation including:
    - Required field checking
    - Value format validation
    - Application-specific requirements
    - Environment variable validation
    - Cross-field dependencies
    """
    
    # Core GAM API requirements (all applications)
    CORE_REQUIRED_FIELDS = {
        'gam.network_code': 'Google Ad Manager network code',
        'auth.type': 'Authentication type (oauth2 or service_account)',
    }
    
    # OAuth2 specific requirements
    OAUTH2_REQUIRED_FIELDS = {
        'auth.oauth2.client_id': 'OAuth2 client ID',
        'auth.oauth2.client_secret': 'OAuth2 client secret',
        'auth.oauth2.refresh_token': 'OAuth2 refresh token',
    }
    
    # Service account specific requirements
    SERVICE_ACCOUNT_REQUIRED_FIELDS = {
        'auth.service_account.path': 'Service account JSON file path',
    }
    
    # Application-specific required fields
    APPLICATION_REQUIRED_FIELDS = {
        ApplicationType.MCP_SERVER: {
            'mcp.enabled': 'MCP server enabled flag',
        },
        ApplicationType.REPORT_BUILDER: {
            'report_builder.enabled': 'Report builder enabled flag',
            'report_builder.frontend_url': 'Frontend URL for CORS',
        },
        ApplicationType.API_SERVER: {
            'api_server.enabled': 'API server enabled flag',
            'api_server.api_key': 'API authentication key',
        },
        ApplicationType.CLI: {
            'cli.enabled': 'CLI enabled flag',
        },
        ApplicationType.SDK: {
            'sdk.enabled': 'SDK enabled flag',
        }
    }
    
    # Optional but recommended fields
    RECOMMENDED_FIELDS = {
        'gam.application_name': 'Application identification name',
        'gam.timezone': 'Default timezone for reports',
        'api.preference': 'Preferred API type (soap/rest)',
        'logging.level': 'Logging level',
        'performance.cache.enabled': 'Enable caching for performance',
    }
    
    # Valid enum values for validation
    VALID_VALUES = {
        'auth.type': ['oauth2', 'service_account'],
        'api.preference': [None, 'soap', 'rest'],
        'logging.level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'mcp.transport': ['stdio', 'http'],
        'performance.cache.backend': ['file', 'memory', 'redis'],
        'report_builder.templates.storage_type': ['file', 'database'],
    }
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate_for_app(self, config: Dict[str, Any], app_type: str) -> List[ValidationIssue]:
        """
        Validate configuration for specific application type.
        
        Args:
            config: Configuration dictionary to validate
            app_type: Application type string
            
        Returns:
            List of validation issues found
        """
        self.issues = []
        
        try:
            app_enum = ApplicationType(app_type)
        except ValueError:
            valid_apps = [app.value for app in ApplicationType]
            self.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "application_type",
                f"Unknown application type '{app_type}'",
                f"Valid types: {', '.join(valid_apps)}"
            ))
            return self.issues
        
        logger.info(f"Validating configuration for {app_type}")
        
        # Validate core requirements
        self._validate_core_requirements(config)
        
        # Validate authentication configuration
        self._validate_authentication(config)
        
        # Validate application-specific requirements
        self._validate_application_specific(config, app_enum)
        
        # Validate optional but recommended fields
        self._validate_recommended_fields(config)
        
        # Validate value formats and ranges
        self._validate_value_formats(config)
        
        # Validate cross-field dependencies
        self._validate_dependencies(config, app_enum)
        
        # Validate environment variable availability
        self._validate_environment_variables(config)
        
        return self.issues
    
    def _validate_core_requirements(self, config: Dict[str, Any]):
        """Validate core GAM API requirements."""
        for field_path, description in self.CORE_REQUIRED_FIELDS.items():
            value = self._get_nested_value(config, field_path)
            
            if value is None or (isinstance(value, str) and not value.strip()):
                self.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    field_path,
                    f"Required field missing: {description}",
                    f"Set {field_path} in configuration or use environment variable"
                ))
    
    def _validate_authentication(self, config: Dict[str, Any]):
        """Validate authentication configuration."""
        auth_type = self._get_nested_value(config, 'auth.type')
        
        if auth_type == 'oauth2':
            for field_path, description in self.OAUTH2_REQUIRED_FIELDS.items():
                value = self._get_nested_value(config, field_path)
                
                if value is None or (isinstance(value, str) and not value.strip()):
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        field_path,
                        f"Required OAuth2 field missing: {description}",
                        "Ensure all OAuth2 credentials are configured"
                    ))
                elif field_path.endswith('refresh_token') and isinstance(value, str):
                    # Basic refresh token format validation
                    if not value.startswith('1//') and len(value) < 50:
                        self.issues.append(ValidationIssue(
                            ValidationSeverity.WARNING,
                            field_path,
                            "Refresh token format appears invalid",
                            "Verify token was generated correctly using OAuth2 flow"
                        ))
        
        elif auth_type == 'service_account':
            for field_path, description in self.SERVICE_ACCOUNT_REQUIRED_FIELDS.items():
                value = self._get_nested_value(config, field_path)
                
                if value is None or (isinstance(value, str) and not value.strip()):
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        field_path,
                        f"Required service account field missing: {description}",
                        "Provide path to service account JSON file"
                    ))
                elif isinstance(value, str):
                    # Check if file exists
                    expanded_path = os.path.expanduser(os.path.expandvars(value))
                    if not os.path.exists(expanded_path):
                        self.issues.append(ValidationIssue(
                            ValidationSeverity.ERROR,
                            field_path,
                            f"Service account file not found: {expanded_path}",
                            "Verify file path and ensure file exists"
                        ))
    
    def _validate_application_specific(self, config: Dict[str, Any], app_type: ApplicationType):
        """Validate application-specific requirements."""
        app_requirements = self.APPLICATION_REQUIRED_FIELDS.get(app_type, {})
        
        for field_path, description in app_requirements.items():
            value = self._get_nested_value(config, field_path)
            
            if value is None:
                self.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    field_path,
                    f"Required {app_type.value} field missing: {description}",
                    f"Configure {field_path} for {app_type.value}"
                ))
        
        # Application-specific validation logic
        if app_type == ApplicationType.MCP_SERVER:
            self._validate_mcp_server(config)
        elif app_type == ApplicationType.REPORT_BUILDER:
            self._validate_report_builder(config)
        elif app_type == ApplicationType.API_SERVER:
            self._validate_api_server(config)
    
    def _validate_mcp_server(self, config: Dict[str, Any]):
        """Validate MCP server specific configuration."""
        mcp_config = config.get('mcp', {})
        
        transport = mcp_config.get('transport', 'stdio')
        if transport == 'http':
            port = mcp_config.get('port')
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    'mcp.port',
                    "Invalid port for HTTP transport",
                    "Set mcp.port to valid port number (1-65535)"
                ))
            
            auth_enabled = mcp_config.get('auth_enabled', False)
            if auth_enabled and not mcp_config.get('jwt'):
                self.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    'mcp.jwt',
                    "JWT configuration missing for authenticated HTTP transport",
                    "Configure JWT settings for secure HTTP transport"
                ))
    
    def _validate_report_builder(self, config: Dict[str, Any]):
        """Validate Report Builder specific configuration."""
        rb_config = config.get('report_builder', {})
        
        # Validate frontend URL format
        frontend_url = rb_config.get('frontend_url', '')
        if frontend_url and not (frontend_url.startswith('http://') or frontend_url.startswith('https://')):
            self.issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                'report_builder.frontend_url',
                "Frontend URL should include protocol (http:// or https://)",
                "Add protocol prefix to frontend URL"
            ))
        
        # Validate backend port
        backend_config = rb_config.get('backend', {})
        port = backend_config.get('port')
        if isinstance(port, int) and (port < 1 or port > 65535):
            self.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                'report_builder.backend.port',
                "Invalid backend port number",
                "Set port to valid range (1-65535)"
            ))
        
        # Validate template storage
        templates = rb_config.get('templates', {})
        storage_type = templates.get('storage_type', 'file')
        if storage_type == 'file':
            storage_path = templates.get('storage_path')
            if storage_path:
                expanded_path = os.path.expanduser(os.path.expandvars(storage_path))
                parent_dir = os.path.dirname(expanded_path)
                if not os.path.exists(parent_dir):
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        'report_builder.templates.storage_path',
                        f"Template storage parent directory does not exist: {parent_dir}",
                        "Directory will be created automatically"
                    ))
    
    def _validate_api_server(self, config: Dict[str, Any]):
        """Validate API Server specific configuration."""
        api_config = config.get('api_server', {})
        
        # Validate API key
        api_key = api_config.get('api_key')
        if isinstance(api_key, str) and len(api_key) < 16:
            self.issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                'api_server.api_key',
                "API key appears too short for security",
                "Use a longer, more secure API key"
            ))
        
        # Validate port
        port = api_config.get('port')
        if isinstance(port, int) and (port < 1 or port > 65535):
            self.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                'api_server.port',
                "Invalid API server port number",
                "Set port to valid range (1-65535)"
            ))
    
    def _validate_recommended_fields(self, config: Dict[str, Any]):
        """Validate optional but recommended fields."""
        for field_path, description in self.RECOMMENDED_FIELDS.items():
            value = self._get_nested_value(config, field_path)
            
            if value is None:
                self.issues.append(ValidationIssue(
                    ValidationSeverity.INFO,
                    field_path,
                    f"Recommended field not set: {description}",
                    f"Consider setting {field_path} for optimal configuration"
                ))
    
    def _validate_value_formats(self, config: Dict[str, Any]):
        """Validate value formats and enums."""
        for field_path, valid_values in self.VALID_VALUES.items():
            value = self._get_nested_value(config, field_path)
            
            if value is not None and value not in valid_values:
                self.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    field_path,
                    f"Invalid value '{value}'",
                    f"Valid values: {', '.join(str(v) for v in valid_values if v is not None)}"
                ))
        
        # Validate numeric ranges
        numeric_validations = {
            'gam.timeout_seconds': (30, 3600),
            'api.timeout_seconds': (5, 300),
            'api.max_retries': (0, 10),
            'performance.cache.ttl': (60, 86400),  # 1 minute to 24 hours
            'performance.cache.max_size_mb': (10, 10240),  # 10MB to 10GB
        }
        
        for field_path, (min_val, max_val) in numeric_validations.items():
            value = self._get_nested_value(config, field_path)
            
            if isinstance(value, (int, float)):
                if value < min_val or value > max_val:
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        field_path,
                        f"Value {value} outside recommended range",
                        f"Recommended range: {min_val}-{max_val}"
                    ))
    
    def _validate_dependencies(self, config: Dict[str, Any], app_type: ApplicationType):
        """Validate cross-field dependencies."""
        
        # Cache dependencies
        cache_enabled = self._get_nested_value(config, 'performance.cache.enabled')
        if cache_enabled:
            cache_backend = self._get_nested_value(config, 'performance.cache.backend')
            
            if cache_backend == 'file':
                cache_dir = self._get_nested_value(config, 'performance.cache.directory')
                if not cache_dir:
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        'performance.cache.directory',
                        "Cache directory not specified for file backend",
                        "Specify cache directory or use default 'cache'"
                    ))
        
        # MCP transport dependencies
        if app_type == ApplicationType.MCP_SERVER:
            transport = self._get_nested_value(config, 'mcp.transport')
            if transport == 'http':
                host = self._get_nested_value(config, 'mcp.host')
                port = self._get_nested_value(config, 'mcp.port')
                
                if not host:
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        'mcp.host',
                        "Host not specified for HTTP transport",
                        "Set mcp.host (e.g., '0.0.0.0' for all interfaces)"
                    ))
    
    def _validate_environment_variables(self, config: Dict[str, Any]):
        """Validate that environment variables are available when referenced."""
        # Check for environment variable placeholders
        env_var_fields = [
            ('gam.network_code', 'GAM_NETWORK_CODE'),
            ('auth.oauth2.client_id', 'GOOGLE_OAUTH_CLIENT_ID'),
            ('auth.oauth2.client_secret', 'GOOGLE_OAUTH_CLIENT_SECRET'),
            ('auth.oauth2.refresh_token', 'GOOGLE_OAUTH_REFRESH_TOKEN'),
        ]
        
        for field_path, env_var in env_var_fields:
            value = self._get_nested_value(config, field_path)
            
            # Check if value is an environment variable placeholder
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var_name = value[2:-1]
                if not os.getenv(env_var_name):
                    self.issues.append(ValidationIssue(
                        ValidationSeverity.ERROR,
                        field_path,
                        f"Environment variable not set: {env_var_name}",
                        f"Set environment variable: export {env_var_name}=<value>"
                    ))
            elif not value and os.getenv(env_var):
                self.issues.append(ValidationIssue(
                    ValidationSeverity.INFO,
                    field_path,
                    f"Environment variable {env_var} available but not used",
                    f"Consider using ${{{env_var}}} in configuration"
                ))
    
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get nested configuration value using dot notation."""
        keys = path.split('.')
        current = config
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        
        return current
    
    def get_summary(self) -> Dict[str, int]:
        """Get validation summary with counts by severity."""
        summary = {
            'errors': len([i for i in self.issues if i.severity == ValidationSeverity.ERROR]),
            'warnings': len([i for i in self.issues if i.severity == ValidationSeverity.WARNING]),
            'info': len([i for i in self.issues if i.severity == ValidationSeverity.INFO]),
            'total': len(self.issues)
        }
        return summary
    
    def has_errors(self) -> bool:
        """Check if validation found any errors."""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if validation found any warnings."""
        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)


def validate_config(config: Dict[str, Any], app_type: str) -> List[ValidationIssue]:
    """
    Convenience function to validate configuration.
    
    Args:
        config: Configuration dictionary to validate
        app_type: Application type string
        
    Returns:
        List of validation issues
    """
    validator = ConfigValidator()
    return validator.validate_for_app(config, app_type)


def print_validation_results(issues: List[ValidationIssue], show_info: bool = True):
    """
    Print validation results in a formatted way.
    
    Args:
        issues: List of validation issues
        show_info: Whether to show informational messages
    """
    if not issues:
        print("✅ Configuration validation passed!")
        return
    
    # Group issues by severity
    errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
    warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
    info = [i for i in issues if i.severity == ValidationSeverity.INFO]
    
    # Print summary
    print(f"\n📊 Validation Results:")
    print(f"   Errors: {len(errors)}")
    print(f"   Warnings: {len(warnings)}")
    print(f"   Info: {len(info)}")
    print("=" * 60)
    
    # Print errors first
    if errors:
        print("\n🔴 ERRORS (must be fixed):")
        for issue in errors:
            print(f"  {issue}")
    
    # Print warnings
    if warnings:
        print("\n🟡 WARNINGS (should be addressed):")
        for issue in warnings:
            print(f"  {issue}")
    
    # Print info if requested
    if info and show_info:
        print("\n🔵 INFORMATION (optional improvements):")
        for issue in info:
            print(f"  {issue}")
    
    print()