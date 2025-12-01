"""
Server module shim that imports from applications/mcp-server/server.py
"""

import sys
from pathlib import Path

# Add mcp-server directory to path
_mcp_server_path = Path(__file__).parent.parent / "mcp-server"
if str(_mcp_server_path) not in sys.path:
    sys.path.insert(0, str(_mcp_server_path))

# Import everything from the actual server module
from server import *  # noqa: F401, F403
from server import (
    create_mcp_server,
    get_server,
    _gam_quick_report,
    _gam_list_reports,
    _gam_get_dimensions_metrics,
    _gam_get_common_combinations,
    _gam_get_quick_report_types,
)

__all__ = [
    "create_mcp_server",
    "get_server",
    "_gam_quick_report",
    "_gam_list_reports",
    "_gam_get_dimensions_metrics",
    "_gam_get_common_combinations",
    "_gam_get_quick_report_types",
]
