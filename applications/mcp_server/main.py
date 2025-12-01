"""
Import shim for main entry point.

This allows importing from 'applications.mcp_server.main' even though
the actual file is in 'applications/mcp-server/main.py'.
"""

import sys
from pathlib import Path

# Add mcp-server directory to path
_mcp_server_path = Path(__file__).parent.parent / "mcp-server"
if str(_mcp_server_path) not in sys.path:
    sys.path.insert(0, str(_mcp_server_path))

# Import and re-export main function
from main import main

__all__ = ["main"]

# Allow running as a module
if __name__ == "__main__":
    main()
