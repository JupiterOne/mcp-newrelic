"""GraphQL utility functions for data extraction and query building."""

from typing import Any


def extract_nested_data(result: dict[str, Any], path: list[str]) -> dict[str, Any]:
    """Extract nested data from GraphQL result following a path"""
    current = result
    for key in path:
        current = current.get(key, {})
    return current


def extract_alert_data(result: dict[str, Any], endpoint: str) -> dict[str, Any]:
    """Extract alert-related data from GraphQL result"""
    return extract_nested_data(result, ["data", "actor", "account", "alerts", endpoint])


def extract_notification_data(result: dict[str, Any], endpoint: str) -> dict[str, Any]:
    """Extract notification-related data from GraphQL result"""
    return extract_nested_data(result, ["data", "actor", "account", "aiNotifications", endpoint])


def extract_workflow_data(result: dict[str, Any]) -> dict[str, Any]:
    """Extract workflow data from GraphQL result"""
    return extract_nested_data(result, ["data", "actor", "account", "aiWorkflows", "workflows"])


def build_actor_query(account_id: str, query_body: str) -> str:
    """Build standard actor-based GraphQL query"""
    return f"""
    query {{
      actor {{
        account(id: {account_id}) {{
          {query_body}
        }}
      }}
    }}
    """


def build_alerts_query(account_id: str, endpoint: str, fields: str) -> str:
    """Build alerts-specific GraphQL query"""
    query_body = f"""
    alerts {{
      {endpoint} {{
        {fields}
      }}
    }}
    """
    return build_actor_query(account_id, query_body)
