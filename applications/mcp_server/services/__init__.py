"""MCP Server services (import shim for hyphenated directory)."""

# Direct import from the actual hyphenated directory
import sys
from pathlib import Path

# Get the actual mcp-server/services directory
services_dir = Path(__file__).parent.parent.parent / "mcp-server" / "services"

# Import the actual module by reading and executing it
import importlib.util

def _load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load report_service from the actual location
_report_service = _load_module("report_service", services_dir / "report_service.py")

# Re-export
ReportService = _report_service.ReportService

__all__ = ["ReportService"]
