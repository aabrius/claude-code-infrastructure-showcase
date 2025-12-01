"""
Package shim for mcp-server directory.

This package allows importing from 'applications.mcp_server' even though
the actual directory is named 'mcp-server' (with hyphen).
"""

import sys
from pathlib import Path

# Add mcp-server directory to path
_mcp_server_path = Path(__file__).parent.parent / "mcp-server"
if str(_mcp_server_path) not in sys.path:
    sys.path.insert(0, str(_mcp_server_path))

# Re-export all public symbols from the actual mcp-server package
try:
    from server import create_mcp_server, get_server
    from settings import MCPSettings, get_settings

    __all__ = [
        "create_mcp_server",
        "get_server",
        "MCPSettings",
        "get_settings",
    ]

    __version__ = "2.0.0"
except ImportError:
    # Allow partial import if dependencies aren't available
    __all__ = []
    __version__ = "2.0.0"
