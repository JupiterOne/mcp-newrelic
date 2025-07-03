"""
Configuration management for New Relic MCP Server.

Handles loading configuration from environment variables, JSON files, and command line arguments
with proper priority hierarchy.
"""

import argparse
import json
import os
from pathlib import Path


class NewRelicConfig:
    """Configuration for New Relic MCP Server"""

    def __init__(self):
        self.api_key: str | None = None
        self.account_id: str | None = None
        self.region: str = "US"
        self.timeout: int = 30

    @classmethod
    def from_file(cls, config_path: str) -> "NewRelicConfig":
        """Load configuration from JSON file"""
        config = cls()
        if Path(config_path).exists():
            with open(config_path) as f:
                data = json.load(f)
                config.api_key = data.get("api_key")
                config.account_id = data.get("account_id")
                config.region = data.get("region", "US")
                config.timeout = data.get("timeout", 30)
        return config

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "NewRelicConfig":
        """Load configuration from command line arguments"""
        config = cls()
        config.api_key = args.api_key
        config.account_id = args.account_id
        config.region = args.region
        config.timeout = args.timeout
        return config

    @classmethod
    def from_env(cls) -> "NewRelicConfig":
        """Load configuration from environment variables"""
        config = cls()
        config.api_key = os.getenv("NEW_RELIC_API_KEY")
        config.account_id = os.getenv("NEW_RELIC_ACCOUNT_ID")
        config.region = os.getenv("NEW_RELIC_REGION", "US")
        config.timeout = int(os.getenv("NEW_RELIC_TIMEOUT", "30"))
        return config

    def merge_with(self, other: "NewRelicConfig") -> "NewRelicConfig":
        """Merge with another config, preferring non-None values from other"""
        merged = NewRelicConfig()
        merged.api_key = other.api_key or self.api_key
        merged.account_id = other.account_id or self.account_id
        merged.region = other.region if other.region != "US" else self.region
        merged.timeout = other.timeout if other.timeout != 30 else self.timeout
        return merged

    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.api_key and self.account_id)

    def __repr__(self) -> str:
        return f"NewRelicConfig(region={self.region}, account_id={self.account_id}, timeout={self.timeout})"
