"""
SOAP adapter for Google Ad Manager API.

This module provides the SOAP implementation of the APIAdapter interface,
offering complete access to all GAM operations through the mature SOAP API.
"""

from .soap_adapter import SOAPAdapter

__all__ = ['SOAPAdapter']