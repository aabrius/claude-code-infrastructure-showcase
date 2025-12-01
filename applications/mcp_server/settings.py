"""
Settings module shim that imports from applications/mcp-server/settings.py
"""

import sys
from pathlib import Path

# Add mcp-server directory to path
_mcp_server_path = Path(__file__).parent.parent / "mcp-server"
if str(_mcp_server_path) not in sys.path:
    sys.path.insert(0, str(_mcp_server_path))

# Import everything from the actual settings module
from settings import *  # noqa: F401, F403
from settings import MCPSettings, get_settings, reset_settings

__all__ = ["MCPSettings", "get_settings", "reset_settings"]
