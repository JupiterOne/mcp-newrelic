"""Base strategy interface for tool handlers"""

from abc import ABC, abstractmethod
from typing import Any

from mcp.types import TextContent

from ...client import NewRelicClient
from ...config import NewRelicConfig


class ToolHandlerStrategy(ABC):
    """Abstract base class for tool handlers"""

    def __init__(self, client: NewRelicClient, config: NewRelicConfig):
        self.client = client
        self.config = config

    @abstractmethod
    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        """Handle the tool execution"""
        pass

    @staticmethod
    def _create_error_response(message: str) -> list[TextContent]:
        """Create standardized error response"""
        return [TextContent(type="text", text=f"Error: {message}")]

    @staticmethod
    def _create_success_response(message: str) -> list[TextContent]:
        """Create standardized success response"""
        return [TextContent(type="text", text=message)]
