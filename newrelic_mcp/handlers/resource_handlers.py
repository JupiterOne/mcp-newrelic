"""
Resource handlers for New Relic MCP Server.

Handles reading of New Relic resources via MCP.
"""

import logging

from mcp.types import Resource
from pydantic import HttpUrl

from ..client import NewRelicClient
from ..config import NewRelicConfig
from ..utils.error_handling import format_resource_error

logger = logging.getLogger(__name__)


class ResourceHandlers:
    """Handles MCP resource operations"""

    def __init__(self, client: NewRelicClient, config: NewRelicConfig):
        self.client = client
        self.config = config

    @staticmethod
    def get_resources() -> list[Resource]:
        """Get list of available resources"""
        return [
            Resource(
                uri=HttpUrl("newrelic://applications"),
                name="New Relic Applications",
                description="List of applications monitored by New Relic",
                mimeType="application/json",
            ),
            Resource(
                uri=HttpUrl("newrelic://incidents/recent"),
                name="Recent Incidents",
                description="Recent incidents from New Relic",
                mimeType="application/json",
            ),
            Resource(
                uri=HttpUrl("newrelic://dashboards"),
                name="New Relic Dashboards",
                description="List of available dashboards",
                mimeType="application/json",
            ),
            Resource(
                uri=HttpUrl("newrelic://alerts/policies"),
                name="Alert Policies",
                description="List of alert policies and their configurations",
                mimeType="application/json",
            ),
            Resource(
                uri=HttpUrl("newrelic://alerts/conditions"),
                name="Alert Conditions",
                description="List of all alert conditions across policies",
                mimeType="application/json",
            ),
            Resource(
                uri=HttpUrl("newrelic://alerts/workflows"),
                name="Alert Workflows",
                description="List of alert workflows and notification configurations",
                mimeType="application/json",
            ),
        ]

    async def read_resource(self, uri: str) -> str:
        """Read a specific New Relic resource"""
        if not self.client or not self.config.account_id:
            raise ValueError(
                "New Relic client not configured. Provide credentials via config file, command line, or environment variables."
            )

        if uri == "newrelic://applications":
            return await self._read_applications()
        elif uri == "newrelic://incidents/recent":
            return await self._read_incidents()
        elif uri == "newrelic://dashboards":
            return await self._read_dashboards()
        elif uri == "newrelic://alerts/policies":
            return await self._read_alert_policies()
        elif uri == "newrelic://alerts/conditions":
            return await self._read_alert_conditions()
        elif uri == "newrelic://alerts/workflows":
            return await self._read_alert_workflows()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")

    async def _read_applications(self) -> str:
        """Read applications resource"""
        apps = await self.client.get_applications(self.config.account_id)
        return f"# New Relic Applications\n\n{len(apps)} applications found:\n\n" + "\n".join(
            [f"- **{app.get('name', 'Unknown')}** (ID: {app.get('appId', 'N/A')})" for app in apps]
        )

    async def _read_incidents(self) -> str:
        """Read incidents resource"""
        incidents = await self.client.get_recent_incidents(self.config.account_id)
        return f"# Recent Incidents\n\n{len(incidents)} incidents found:\n\n" + "\n".join(
            [
                f"- **{inc.get('title', 'Unknown')}** - {inc.get('state', 'Unknown')} - {inc.get('timestamp', 'Unknown')}"
                for inc in incidents
            ]
        )

    async def _read_dashboards(self) -> str:
        """Read dashboards resource"""
        result = await self.client.get_dashboards(self.config.account_id, limit=200)

        # Handle errors
        if "error" in result:
            return format_resource_error(result, "New Relic Dashboards")

        dashboards = result.get("entities", [])

        if not dashboards:
            return "# New Relic Dashboards\n\nNo dashboards found."

        dashboard_list = f"# New Relic Dashboards\n\n{len(dashboards)} dashboards found:\n\n"
        for dashboard in dashboards:
            name = dashboard.get("name", "Unknown")
            guid = dashboard.get("guid", "Unknown")
            created = dashboard.get("createdAt", "Unknown")
            permalink = dashboard.get("permalink", "")

            dashboard_list += f"## {name}\n"
            dashboard_list += f"- **GUID**: {guid}\n"
            dashboard_list += f"- **Created**: {created}\n"
            if permalink:
                dashboard_list += f"- **URL**: {permalink}\n"
            dashboard_list += "\n"

        return dashboard_list

    async def _read_alert_policies(self) -> str:
        """Read alert policies resource"""
        result = await self.client.get_alert_policies(self.config.account_id)

        if "error" in result:
            return format_resource_error(result, "Alert Policies")

        policies = result.get("policies", [])
        total_count = result.get("total_count", 0)

        if not policies:
            return "# Alert Policies\n\nNo alert policies found."

        policies_list = f"# Alert Policies\n\n{total_count} alert policies found:\n\n"
        for policy in policies:
            policies_list += self._format_policy_info(policy)

        return policies_list

    async def _read_alert_conditions(self) -> str:
        """Read alert conditions resource"""
        result = await self.client.get_alert_conditions(self.config.account_id)

        if "error" in result:
            return format_resource_error(result, "Alert Conditions")

        conditions = result.get("conditions", [])
        total_count = result.get("total_count", 0)

        if not conditions:
            return "# Alert Conditions\n\nNo alert conditions found."

        conditions_list = f"# Alert Conditions\n\n{total_count} alert conditions found:\n\n"
        for condition in conditions:
            name = condition.get("name", "Unknown")
            condition_id = condition.get("id", "Unknown")
            policy_id = condition.get("policyId", "Unknown")
            enabled = condition.get("enabled", False)
            nrql_query = condition.get("nrql", {}).get("query", "No query")
            terms = condition.get("terms", [])

            conditions_list += f"## {name}\n"
            conditions_list += f"- **Condition ID**: {condition_id}\n"
            conditions_list += f"- **Policy ID**: {policy_id}\n"
            conditions_list += f"- **Enabled**: {enabled}\n"
            conditions_list += f"- **NRQL Query**: `{nrql_query}`\n"

            if terms:
                term = terms[0]  # Show first term
                threshold = term.get("threshold", "N/A")
                operator = term.get("operator", "N/A")
                priority = term.get("priority", "N/A")
                conditions_list += f"- **Threshold**: {operator} {threshold} ({priority})\n"

            conditions_list += "\n"

        return conditions_list

    async def _read_alert_workflows(self) -> str:
        """Read alert workflows resource"""
        result = await self.client.get_workflows(self.config.account_id)

        if "error" in result:
            return format_resource_error(result, "Alert Workflows")

        workflows = result.get("workflows", [])
        total_count = result.get("total_count", 0)

        if not workflows:
            return "# Alert Workflows\n\nNo alert workflows found."

        workflows_list = f"# Alert Workflows\n\n{total_count} alert workflows found:\n\n"
        for workflow in workflows:
            workflows_list += self._format_workflow_info(workflow)

        return workflows_list

    @staticmethod
    def _format_policy_info(policy: dict) -> str:
        """Format policy information for display"""
        name = policy.get("name", "Unknown")
        policy_id = policy.get("id", "Unknown")
        incident_pref = policy.get("incidentPreference", "Unknown")
        created = policy.get("createdAt", "Unknown")

        result = f"## {name}\n"
        result += f"- **Policy ID**: {policy_id}\n"
        result += f"- **Incident Preference**: {incident_pref}\n"
        result += f"- **Created**: {created}\n\n"
        return result

    @staticmethod
    def _format_workflow_info(workflow: dict) -> str:
        """Format workflow information for display"""
        name = workflow.get("name", "Unknown")
        workflow_id = workflow.get("id", "Unknown")
        enabled = workflow.get("enabled", False)
        destinations = workflow.get("destinationConfigurations", [])
        issues_filter = workflow.get("issuesFilter", {})

        result = f"## {name}\n"
        result += f"- **Workflow ID**: {workflow_id}\n"
        result += f"- **Enabled**: {enabled}\n"
        result += f"- **Destinations**: {len(destinations)} configured\n"

        if destinations:
            result += "- **Destination Details**:\n"
            for dest in destinations[:3]:  # Show first 3
                dest_name = dest.get("name", "Unknown")
                dest_type = dest.get("type", "Unknown")
                result += f"  - {dest_name} ({dest_type})\n"
            if len(destinations) > 3:
                result += f"  - ... and {len(destinations) - 3} more\n"

        filter_name = issues_filter.get("name", "No filter")
        result += f"- **Filter**: {filter_name}\n\n"
        return result
