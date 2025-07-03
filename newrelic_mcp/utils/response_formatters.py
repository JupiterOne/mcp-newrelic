"""Response formatting utilities for consistent API responses."""

from typing import Any


def format_create_response(result: dict[str, Any], id_field: str = "id", **extra_fields) -> dict[str, Any]:
    """Format standardized create response"""
    response = {
        "success": True,
        "id": result.get(id_field),
    }

    # Add the specific ID field for backward compatibility
    if id_field != "id":
        response[id_field] = result.get(id_field)

    # Add any extra fields
    for key, field_name in extra_fields.items():
        if isinstance(field_name, str):
            response[key] = result.get(field_name)
        elif isinstance(field_name, list):
            # Handle nested field access like ["nrql", "query"]
            value = result
            for part in field_name:
                value = value.get(part, {}) if isinstance(value, dict) else {}
            response[key] = value
        else:
            response[key] = field_name

    return response


def format_list_response(items: list[dict[str, Any]], section_title: str,
                        empty_message: str = None) -> str:
    """Format list response for resource handlers"""
    if not items:
        return f"# {section_title}\n\n{empty_message or 'No items found.'}"

    return f"# {section_title}\n\n{len(items)} items found:\n\n"
