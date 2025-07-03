"""
Input validation utilities for New Relic MCP Server.

Provides robust validation to prevent security issues and improve reliability.
"""

import re
from typing import Any


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


class InputValidator:
    """Validates and sanitizes user inputs"""

    # NRQL injection patterns to detect
    DANGEROUS_NRQL_PATTERNS = [
        r";\s*DROP\s+",
        r";\s*DELETE\s+",
        r";\s*UPDATE\s+",
        r";\s*INSERT\s+",
        r"<script\b",
        r"javascript:",
        r"vbscript:",
    ]

    @classmethod
    def validate_account_id(cls, account_id: str) -> str:
        """Validate New Relic account ID format"""
        if not account_id:
            raise ValidationError("Account ID cannot be empty")

        if not account_id.isdigit():
            raise ValidationError("Account ID must be numeric")

        if len(account_id) < 6 or len(account_id) > 12:
            raise ValidationError("Account ID must be between 6-12 digits")

        return account_id

    @classmethod
    def validate_nrql_query(cls, query: str) -> str:
        """Validate and sanitize NRQL query"""
        if not query:
            raise ValidationError("NRQL query cannot be empty")

        if len(query) > 10000:
            raise ValidationError("NRQL query too long (max 10,000 characters)")

        # Check for dangerous patterns
        query_lower = query.lower()
        for pattern in cls.DANGEROUS_NRQL_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                raise ValidationError(f"Query contains potentially dangerous pattern: {pattern}")

        # Basic NRQL syntax validation
        if not re.match(r"^\s*SELECT\s+", query, re.IGNORECASE):
            raise ValidationError("NRQL query must start with SELECT")

        return query.strip()

    @classmethod
    def validate_guid(cls, guid: str) -> str:
        """Validate New Relic GUID format"""
        if not guid:
            raise ValidationError("GUID cannot be empty")

        # New Relic GUIDs are base64-encoded strings
        if not re.match(r"^[A-Za-z0-9+/=]+$", guid):
            raise ValidationError("Invalid GUID format")

        if len(guid) < 10 or len(guid) > 100:
            raise ValidationError("GUID length invalid")

        return guid

    @classmethod
    def validate_app_name(cls, app_name: str) -> str:
        """Validate application name"""
        if not app_name:
            raise ValidationError("Application name cannot be empty")

        if len(app_name) > 200:
            raise ValidationError("Application name too long")

        # Basic sanitization
        return app_name.strip()

    @classmethod
    def validate_time_range(cls, hours: int) -> int:
        """Validate time range parameters"""
        if not isinstance(hours, int):
            raise ValidationError("Time range must be an integer")

        if hours < 1:
            raise ValidationError("Time range must be at least 1 hour")

        if hours > 8760:  # 1 year
            raise ValidationError("Time range cannot exceed 1 year")

        return hours

    @classmethod
    def sanitize_arguments(cls, arguments: dict[str, Any]) -> dict[str, Any]:
        """Sanitize all arguments in a request"""
        sanitized = {}

        for key, value in arguments.items():
            if isinstance(value, str):
                # Remove null bytes and control characters
                value = re.sub(r"[\x00-\x1f\x7f]", "", value)
                value = value.strip()

            sanitized[key] = value

        return sanitized
