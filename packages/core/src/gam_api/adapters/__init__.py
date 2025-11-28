"""
Google Ad Manager API adapters.

This package provides adapter implementations for different GAM API backends,
following the adapter pattern to ensure consistent behavior across SOAP and REST APIs.
"""

from .base import APIAdapter
from .soap.soap_adapter import SOAPAdapter

__all__ = ['APIAdapter', 'SOAPAdapter']