"""
Compatibility layer for GAMUnifiedClient imports.

This module provides backward compatibility for code that imports GAMUnifiedClient
from the old src.core.unified.client location.
"""

import warnings
import sys
import os

# Add gam_api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def _deprecation_warning():
    """Issue deprecation warning for old import."""
    warnings.warn(
        "Importing GAMUnifiedClient from 'src.core.unified.client' is deprecated. "
        "Please use 'from gam_api import GAMClient' instead. "
        "The old import will be removed in a future version.",
        DeprecationWarning,
        stacklevel=3
    )

# Import the new client and create an alias
try:
    from gam_api import GAMClient as _NewGAMClient
    
    class GAMUnifiedClient(_NewGAMClient):
        """
        Backward compatibility wrapper for GAMUnifiedClient.
        
        This class is deprecated. Use gam_api.GAMClient instead.
        """
        
        def __init__(self, *args, **kwargs):
            _deprecation_warning()
            super().__init__(*args, **kwargs)
    
    # Also create the factory function for compatibility
    def create_unified_client(*args, **kwargs):
        """
        Factory function for creating GAMUnifiedClient (deprecated).
        
        Use gam_api.create_client() instead.
        """
        _deprecation_warning()
        from gam_api import create_client
        return create_client(*args, **kwargs)

except ImportError:
    # Fallback if gam_api is not available
    class GAMUnifiedClient:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "GAMUnifiedClient is no longer available from this location. "
                "Please install and use 'from gam_api import GAMClient' instead."
            )
    
    def create_unified_client(*args, **kwargs):
        raise ImportError(
            "create_unified_client is no longer available from this location. "
            "Please install and use 'from gam_api import create_client' instead."
        )

__all__ = ['GAMUnifiedClient', 'create_unified_client']