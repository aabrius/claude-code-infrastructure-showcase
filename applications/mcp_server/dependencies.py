"""Import shim for applications.mcp_server.dependencies"""
import sys
from importlib import import_module

# Import from hyphenated directory using importlib
_mod = import_module('applications.mcp-server.dependencies')

# Re-export all public symbols
lifespan = _mod.lifespan
get_report_service = _mod.get_report_service
get_gam_client = _mod.get_gam_client
get_cache = _mod.get_cache

__all__ = ['lifespan', 'get_report_service', 'get_gam_client', 'get_cache']
