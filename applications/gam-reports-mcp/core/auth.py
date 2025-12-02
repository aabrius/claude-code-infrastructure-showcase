"""Standalone OAuth2 authentication for GAM REST API."""

from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class AuthConfig(BaseModel):
    """Authentication configuration."""

    client_id: str
    client_secret: str
    refresh_token: str
    network_code: str


class GAMAuth:
    """Standalone OAuth2 authentication for GAM Reports MCP."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".googleads.yaml"
        self._credentials: Credentials | None = None
        self._config: AuthConfig | None = None

    @property
    def config(self) -> AuthConfig:
        """Load and cache configuration."""
        if self._config is None:
            data = yaml.safe_load(self.config_path.read_text())
            ad_manager: dict[str, Any] = data.get("ad_manager", {})
            self._config = AuthConfig(
                client_id=ad_manager["client_id"],
                client_secret=ad_manager["client_secret"],
                refresh_token=ad_manager["refresh_token"],
                network_code=str(ad_manager["network_code"]),
            )
        return self._config

    @property
    def network_code(self) -> str:
        """Get network code from configuration."""
        return self.config.network_code

    def get_credentials(self) -> Credentials:
        """Get OAuth2 credentials, refreshing if needed."""
        if self._credentials is None:
            self._credentials = Credentials(
                None,
                refresh_token=self.config.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
            self._credentials.refresh(Request())

        if self._credentials.expired:
            self._credentials.refresh(Request())

        return self._credentials
