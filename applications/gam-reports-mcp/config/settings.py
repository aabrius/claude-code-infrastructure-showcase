# config/settings.py
"""Application settings from environment."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GAM Configuration
    network_code: str = Field(default="", alias="GAM_NETWORK_CODE")
    credentials_path: Path = Field(
        default=Path.home() / ".googleads.yaml",
        alias="GOOGLE_ADS_YAML",
    )

    # MCP Server
    mcp_transport: str = Field(default="stdio", alias="MCP_TRANSPORT")
    mcp_port: int = Field(default=8080, alias="MCP_PORT")

    # JWT Auth (for Cloud Run)
    auth_enabled: bool = Field(default=False, alias="MCP_AUTH_ENABLED")
    jwt_secret: str = Field(default="", alias="JWT_SECRET")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
