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
