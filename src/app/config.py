"""
Application Configuration Module
Loads settings securely from environment variables with sensible production defaults.
"""

import os
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "secure-cloud-service"))
    app_version: str = Field(default_factory=lambda: os.getenv("APP_VERSION", "1.2.0"))
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    enable_chaos: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_CHAOS", "false").lower() in ("true", "1", "yes")
    )
    commit_sha: str = Field(default_factory=lambda: os.getenv("COMMIT_SHA", "dev-local-build"))
    aws_region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))


def get_config() -> AppConfig:
    """Return an instantiated configuration singleton."""
    return AppConfig()
