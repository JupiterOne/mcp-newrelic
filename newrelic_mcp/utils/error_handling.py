"""Common error handling utilities for New Relic MCP Server."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def handle_api_error(operation_name: str, exception: Exception) -> dict[str, Any]:
    """Standardized error handling for API operations"""
    logger.error(f"{operation_name} failed: {exception}")
    return {"error": str(exception)}


def check_result_error(result: dict[str, Any], operation_name: str) -> dict[str, Any] | None:
    """Check if result contains error and return formatted error response"""
    if "error" in result:
        return {"error": f"Failed to {operation_name}: {result['error']}"}
    return None


def handle_graphql_notification_errors(create_result: dict[str, Any], operation_name: str) -> dict[str, Any] | None:
    """Handle GraphQL notification API errors"""
    if create_result.get("errors"):
        errors = create_result["errors"]
        if errors:
            error = errors[0]
            error_type = error.get("__typename", "Unknown")
            error_msg = error.get("description", error.get("type", f"Error type: {error_type}"))
            return {"error": f"{operation_name} failed: {error_msg}"}
    return None


def format_resource_error(result: dict[str, Any], section_title: str) -> str:
    """Format error response for resource handlers"""
    return f"# {section_title}\n\nError: {result['error']}"
