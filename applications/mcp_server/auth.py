"""
Import shim for auth module.

This module provides backward-compatible imports by proxying to the
actual implementation in applications/mcp-server/auth.py
"""

import sys
import importlib.util
from pathlib import Path

# Get the path to the actual implementation
current_dir = Path(__file__).parent
auth_path = current_dir.parent / "mcp-server" / "auth.py"

# Load the module from the file
spec = importlib.util.spec_from_file_location("_auth_impl", auth_path)
_auth_impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_auth_impl)

# Re-export everything from the implementation
create_auth_provider = _auth_impl.create_auth_provider

__all__ = ["create_auth_provider"]
