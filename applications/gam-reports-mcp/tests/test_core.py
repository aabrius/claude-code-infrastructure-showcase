# tests/test_core.py
import pytest
from pathlib import Path
from core.auth import GAMAuth, AuthConfig


def test_auth_config_model():
    config = AuthConfig(
        client_id="test-client-id",
        client_secret="test-secret",
        refresh_token="test-refresh",
        network_code="123456",
    )
    assert config.client_id == "test-client-id"
    assert config.network_code == "123456"


def test_gam_auth_loads_config(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "123456"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.config.client_id == "test-client-id"
    assert auth.network_code == "123456"


def test_gam_auth_network_code_property(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "789"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.network_code == "789"
