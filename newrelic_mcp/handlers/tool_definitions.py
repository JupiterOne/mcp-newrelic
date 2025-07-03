"""
Tool definitions for New Relic MCP Server.

Centralized definition of all available tools and their schemas.
"""

from mcp.types import Tool


def get_monitoring_tools():
    """Get monitoring and performance tools"""
    return [
        Tool(
            name="query_nrql",
            description="Execute a NRQL query against New Relic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "NRQL query to execute"},
                    "account_id": {
                        "type": "string",
                        "description": "New Relic account ID (optional, uses default if not provided)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_app_performance",
            description="Get performance metrics for a specific application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"},
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 1)",
                        "default": 1,
                    },
                },
                "required": ["app_name"],
            },
        ),
        Tool(
            name="get_app_errors",
            description="Get error metrics for a specific application",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"},
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 1)",
                        "default": 1,
                    },
                },
                "required": ["app_name"],
            },
        ),
        Tool(
            name="get_incidents",
            description="Get recent incidents from New Relic",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 24)",
                        "default": 24,
                    }
                },
            },
        ),
        Tool(
            name="get_infrastructure_hosts",
            description="Get infrastructure hosts and their metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 1)",
                        "default": 1,
                    }
                },
            },
        ),
        Tool(
            name="get_alert_violations",
            description="Get recent alert violations and incidents",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 24)",
                        "default": 24,
                    }
                },
            },
        ),
        Tool(
            name="get_deployments",
            description="Get deployment markers and their impact",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application (optional, gets all deployments if not provided)",
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back (default: 168 = 1 week)",
                        "default": 168,
                    },
                },
            },
        ),
    ]


def get_dashboard_tools():
    """Get dashboard management tools"""
    return [
        Tool(
            name="get_dashboards",
            description="Get New Relic dashboards (max 200 due to API limits). Use search parameter to find specific dashboards efficiently.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search term to filter dashboards by name (case-insensitive). Recommended for large accounts.",
                    },
                    "guid": {"type": "string", "description": "Specific dashboard GUID to retrieve"},
                    "limit": {
                        "type": "integer",
                        "description": "Number of dashboards to retrieve (default: 200, API max: 200)",
                        "default": 200,
                        "maximum": 200,
                    },
                },
            },
        ),
        Tool(
            name="create_dashboard",
            description="Create a new New Relic dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the dashboard"},
                    "description": {"type": "string", "description": "Description of the dashboard (optional)"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="add_widget_to_dashboard",
            description="Add a widget to an existing dashboard (requires dashboard GUID and widget configuration)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_guid": {"type": "string", "description": "GUID of the dashboard to add widget to"},
                    "widget_title": {"type": "string", "description": "Title for the widget"},
                    "widget_query": {"type": "string", "description": "NRQL query for the widget"},
                    "widget_type": {
                        "type": "string",
                        "description": "Type of widget (line, area, bar, pie, table, billboard, etc.)",
                        "default": "line",
                    },
                },
                "required": ["dashboard_guid", "widget_title", "widget_query"],
            },
        ),
        Tool(
            name="search_all_dashboards",
            description="Search through dashboards with local filtering (retrieves max 200 from API, then searches locally). Better for complex searches.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search term to filter dashboards by name (case-insensitive)",
                    },
                    "guid": {"type": "string", "description": "Specific dashboard GUID to find"},
                },
            },
        ),
        Tool(
            name="get_dashboard_widgets",
            description="Get all widgets from a dashboard with their details and IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_guid": {"type": "string", "description": "Dashboard GUID to get widgets from"}
                },
                "required": ["dashboard_guid"],
            },
        ),
        Tool(
            name="update_widget",
            description="Update an existing widget on a dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_guid": {"type": "string", "description": "Page GUID where the widget is located"},
                    "widget_id": {"type": "string", "description": "Widget ID to update"},
                    "widget_title": {"type": "string", "description": "New title for the widget"},
                    "widget_query": {"type": "string", "description": "New NRQL query for the widget"},
                    "widget_type": {
                        "type": "string",
                        "description": "New widget type (line, area, bar, pie, table, billboard, etc.)",
                        "default": "line",
                    },
                },
                "required": ["page_guid", "widget_id"],
            },
        ),
        Tool(
            name="delete_widget",
            description="Delete a widget from a dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_guid": {"type": "string", "description": "Page GUID where the widget is located"},
                    "widget_id": {"type": "string", "description": "Widget ID to delete"},
                },
                "required": ["page_guid", "widget_id"],
            },
        ),
    ]


def get_alert_tools():
    """Get alert management tools"""
    return [
        Tool(
            name="create_alert_policy",
            description="Create a new alert policy",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the alert policy"},
                    "incident_preference": {
                        "type": "string",
                        "description": "How incidents are created (PER_POLICY, PER_CONDITION, PER_CONDITION_AND_TARGET)",
                        "default": "PER_POLICY",
                        "enum": ["PER_POLICY", "PER_CONDITION", "PER_CONDITION_AND_TARGET"],
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="create_nrql_condition",
            description="Create a NRQL alert condition",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy_id": {"type": "string", "description": "Alert policy ID to attach the condition to"},
                    "name": {"type": "string", "description": "Name of the alert condition"},
                    "description": {"type": "string", "description": "Description of the alert condition (optional)"},
                    "nrql_query": {"type": "string", "description": "NRQL query for the condition"},
                    "threshold": {"type": "number", "description": "Alert threshold value"},
                    "threshold_operator": {
                        "type": "string",
                        "description": "Threshold operator (ABOVE, BELOW, EQUAL)",
                        "default": "ABOVE",
                        "enum": ["ABOVE", "BELOW", "EQUAL"],
                    },
                    "threshold_duration": {
                        "type": "integer",
                        "description": "Duration in seconds for threshold breach (60-7200)",
                        "default": 300,
                        "minimum": 60,
                        "maximum": 7200,
                    },
                    "priority": {
                        "type": "string",
                        "description": "Alert priority (CRITICAL, HIGH, MEDIUM, LOW)",
                        "default": "CRITICAL",
                        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    },
                    "aggregation_window": {
                        "type": "integer",
                        "description": "Aggregation window in seconds (30-1200)",
                        "default": 60,
                        "minimum": 30,
                        "maximum": 1200,
                    },
                },
                "required": ["policy_id", "name", "nrql_query", "threshold"],
            },
        ),
        Tool(
            name="create_notification_destination",
            description="Create a notification destination (email, webhook, Slack, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the destination"},
                    "type": {
                        "type": "string",
                        "description": "Type of destination (EMAIL, WEBHOOK, SLACK, etc.)",
                        "enum": ["EMAIL", "WEBHOOK", "SLACK", "PAGERDUTY", "SERVICE_NOW"],
                    },
                    "properties": {
                        "type": "object",
                        "description": "Destination-specific properties (e.g., email address, webhook URL)",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["name", "type", "properties"],
            },
        ),
        Tool(
            name="create_notification_channel",
            description="Create a notification channel linked to a destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the notification channel"},
                    "destination_id": {"type": "string", "description": "ID of the destination to link to"},
                    "product": {
                        "type": "string",
                        "description": "Product type (IINT for Applied Intelligence)",
                        "default": "IINT",
                    },
                    "type": {
                        "type": "string",
                        "description": "Channel type (EMAIL, WEBHOOK, SLACK, etc.)",
                        "enum": ["EMAIL", "WEBHOOK", "SLACK", "PAGERDUTY", "SERVICE_NOW"],
                    },
                    "properties": {
                        "type": "object",
                        "description": "Channel-specific properties",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["name", "destination_id", "type"],
            },
        ),
        Tool(
            name="create_workflow",
            description="Create a workflow to connect alert policies to notification channels",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the workflow"},
                    "channel_ids": {
                        "type": "array",
                        "description": "List of notification channel IDs to send alerts to",
                        "items": {"type": "string"},
                    },
                    "filter_name": {
                        "type": "string",
                        "description": "Name for the issues filter (optional)",
                        "default": "Filter-name",
                    },
                    "filter_predicates": {
                        "type": "array",
                        "description": "Filter predicates to determine which alerts trigger this workflow",
                        "items": {
                            "type": "object",
                            "properties": {
                                "attribute": {"type": "string"},
                                "operator": {
                                    "type": "string",
                                    "enum": ["EQUAL", "NOT_EQUAL", "IN", "NOT_IN", "CONTAINS", "DOES_NOT_CONTAIN"],
                                },
                                "values": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["attribute", "operator", "values"],
                        },
                    },
                    "enabled": {"type": "boolean", "description": "Whether the workflow is enabled", "default": True},
                },
                "required": ["name", "channel_ids"],
            },
        ),
        Tool(
            name="list_alert_policies",
            description="List all alert policies in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_alert_conditions",
            description="List alert conditions, optionally filtered by policy",
            inputSchema={
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "Policy ID to filter conditions (optional, shows all if not provided)",
                    }
                },
            },
        ),
        Tool(
            name="list_notification_destinations",
            description="List all notification destinations",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_notification_channels",
            description="List all notification channels",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_workflows",
            description="List all alert workflows",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


def get_all_tools():
    """Get all available tools"""
    return get_monitoring_tools() + get_dashboard_tools() + get_alert_tools()
