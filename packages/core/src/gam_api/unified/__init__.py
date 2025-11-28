"""
Unified Google Ad Manager Client

DEPRECATED: This module is kept for backward compatibility only.
Please use the new gam_api package instead:

    # Old (deprecated)
    from src.core.unified import GAMUnifiedClient
    
    # New (recommended)  
    from gam_api import GAMClient

This module provides a unified interface that intelligently selects between
SOAP and REST APIs based on operation type, with automatic fallback and
retry mechanisms.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "The src.core.unified module is deprecated. "
    "Please use 'from gam_api import GAMClient' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import original implementations for backward compatibility
from .client import GAMUnifiedClient, create_unified_client
from .strategy import APISelectionStrategy, OperationType
from .fallback import FallbackManager
from ..config import UnifiedClientConfig

# Also import compatibility layer
from .compatibility import GAMUnifiedClient as CompatGAMUnifiedClient
from .compatibility import create_unified_client as compat_create_unified_client

# Override with compatibility versions that issue warnings
GAMUnifiedClient = CompatGAMUnifiedClient
create_unified_client = compat_create_unified_client

__all__ = [
    'GAMUnifiedClient',
    'create_unified_client',
    'APISelectionStrategy', 
    'OperationType',
    'FallbackManager',
    'UnifiedClientConfig'
]

__version__ = '1.0.0'