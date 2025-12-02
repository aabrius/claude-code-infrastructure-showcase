# tests/test_config.py
import pytest
from pathlib import Path
from config.settings import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.mcp_transport == "stdio"
    assert settings.mcp_port == 8080
    assert settings.auth_enabled is False


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_PORT", "9000")
    monkeypatch.setenv("MCP_AUTH_ENABLED", "true")

    settings = Settings()
    assert settings.mcp_transport == "http"
    assert settings.mcp_port == 9000
    assert settings.auth_enabled is True
