"""
Advanced configuration management for New Relic MCP Server.

Provides secure, validated configuration with proper secret handling.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..validators import InputValidator, ValidationError

logger = logging.getLogger(__name__)


class NewRelicConfigModel(BaseModel):
    """Pydantic model for validated configuration"""

    api_key: str = Field(..., min_length=40, max_length=50, description="New Relic API key")
    account_id: str = Field(..., description="New Relic account ID")
    region: str = Field(default="US", pattern="^(US|EU)$", description="New Relic region")
    timeout: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    rate_limit: int = Field(default=100, ge=1, le=1000, description="Requests per minute")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")

    @classmethod
    @field_validator("account_id")
    def validate_account_id(cls, v):
        """Validate account ID format"""
        return InputValidator.validate_account_id(v)

    @classmethod
    @field_validator("api_key")
    def validate_api_key(cls, v):
        """Validate API key format"""
        if not v.startswith(("NRAK-", "NRAA-")):
            raise ValueError("API key must start with NRAK- or NRAA-")
        return v

    class Config:
        validate_assignment = True
        extra = "forbid"  # Prevent unknown configuration options


@dataclass
class SecureConfig:
    """Secure configuration container that doesn't expose secrets in logs"""

    _api_key: str = field(repr=False)  # Hidden from repr
    account_id: str
    region: str = "US"
    timeout: int = 30
    rate_limit: int = 100
    retry_attempts: int = 3

    @property
    def api_key(self) -> str:
        """Get API key (for internal use only)"""
        return self._api_key

    @property
    def masked_api_key(self) -> str:
        """Get masked API key for logging"""
        if not self._api_key:
            return "None"
        return f"{self._api_key[:8]}...{self._api_key[-4:]}"

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self._api_key and self.account_id)

    def to_dict(self, include_secrets: bool = False) -> dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "account_id": self.account_id,
            "region": self.region,
            "timeout": self.timeout,
            "rate_limit": self.rate_limit,
            "retry_attempts": self.retry_attempts,
        }

        if include_secrets:
            data["api_key"] = self._api_key
        else:
            data["api_key"] = self.masked_api_key

        return data


class ConfigurationManager:
    """Advanced configuration manager with validation and security"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_config(self, config_path: str | None = None, cli_args: dict[str, Any] | None = None) -> SecureConfig:
        """Load and validate configuration with proper precedence"""

        # 1. Start with environment variables
        env_config = self._load_from_environment()

        # 2. Override with file configuration
        if config_path and os.path.exists(config_path):
            file_config = self._load_from_file(config_path)
            env_config.update(file_config)

        # 3. Override with CLI arguments
        if cli_args:
            sanitized_args = {k: v for k, v in cli_args.items() if v is not None}
            env_config.update(sanitized_args)

        # 4. Validate configuration
        try:
            validated_config = NewRelicConfigModel(**env_config)

            # 5. Create secure config object
            secure_config = SecureConfig(
                _api_key=validated_config.api_key,
                account_id=validated_config.account_id,
                region=validated_config.region,
                timeout=validated_config.timeout,
                rate_limit=validated_config.rate_limit,
                retry_attempts=validated_config.retry_attempts,
            )

            self.logger.info(
                "Configuration loaded successfully",
                extra={
                    "account_id": secure_config.account_id,
                    "region": secure_config.region,
                    "api_key": secure_config.masked_api_key,
                },
            )

            return secure_config

        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise ValidationError(f"Invalid configuration: {e}") from e

    @staticmethod
    def _load_from_environment() -> dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            "api_key": os.getenv("NEW_RELIC_API_KEY"),
            "account_id": os.getenv("NEW_RELIC_ACCOUNT_ID"),
            "region": os.getenv("NEW_RELIC_REGION", "US"),
            "timeout": int(os.getenv("NEW_RELIC_TIMEOUT", "30")),
            "rate_limit": int(os.getenv("NEW_RELIC_RATE_LIMIT", "100")),
            "retry_attempts": int(os.getenv("NEW_RELIC_RETRY_ATTEMPTS", "3")),
        }

    @staticmethod
    def _load_from_file(config_path: str) -> dict[str, Any]:
        """Load configuration from JSON file"""
        import json

        try:
            with open(config_path) as config_file:
                return json.load(config_file)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in config file: {e}") from e
        except Exception as e:
            raise ValidationError(f"Cannot read config file: {e}") from e
