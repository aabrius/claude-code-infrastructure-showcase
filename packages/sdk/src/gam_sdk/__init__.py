"""
Google Ad Manager API Python SDK

A fluent, developer-friendly SDK for Google Ad Manager operations.
Provides chainable methods for report generation, configuration management,
and authentication.

Usage:
    from gam_api.sdk import GAMClient
    
    # Initialize client
    client = GAMClient()
    
    # Generate reports with fluent API
    report = (client
        .reports()
        .delivery()
        .last_30_days()
        .dimensions('DATE', 'AD_UNIT_NAME')
        .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS')
        .execute())
    
    # Export results
    report.to_csv('delivery_report.csv')
    report.to_json('delivery_report.json')
    
    # Configuration management
    config = (client
        .config()
        .set('gam.network_code', '12345678')
        .set('logging.level', 'DEBUG')
        .validate())
"""

from .client import GAMClient
from .reports import ReportBuilder, ReportResult
from .config import ConfigManager
from .auth import AuthManager as SDKAuthManager
from .exceptions import SDKError, ReportError, ConfigError, AuthError

__all__ = [
    'GAMClient',
    'ReportBuilder', 
    'ReportResult',
    'ConfigManager',
    'SDKAuthManager',
    'SDKError',
    'ReportError', 
    'ConfigError',
    'AuthError'
]

__version__ = '1.0.0'