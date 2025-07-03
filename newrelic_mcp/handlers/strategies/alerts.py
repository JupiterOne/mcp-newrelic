"""Alert tool handlers using Strategy pattern"""

from typing import Any

from mcp.types import TextContent

from .base import ToolHandlerStrategy


class CreateAlertPolicyHandler(ToolHandlerStrategy):
    """Handler for creating alert policies"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        name = arguments["name"]
        incident_preference = arguments.get("incident_preference", "PER_POLICY")

        result = await self.client.create_alert_policy(account_id, name, incident_preference)

        if "error" in result:
            return self._create_error_response(f"creating alert policy '{name}': {result['error']}")

        policy_id = result.get("id", "Unknown")
        return self._create_success_response(
            f"Alert policy '{name}' created successfully!\nPolicy ID: {policy_id}\n"
            f"Incident preference: {incident_preference}"
        )


class CreateNRQLConditionHandler(ToolHandlerStrategy):
    """Handler for creating NRQL alert conditions"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        policy_id = arguments["policy_id"]
        name = arguments["name"]
        nrql_query = arguments["nrql_query"]
        threshold = arguments["threshold"]
        threshold_duration = arguments.get("threshold_duration", 300)
        threshold_operator = arguments.get("threshold_operator", "ABOVE")
        priority = arguments.get("priority", "CRITICAL")
        aggregation_window = arguments.get("aggregation_window", 60)
        description = arguments.get("description")

        # Map HIGH/MEDIUM/LOW to WARNING since API only accepts CRITICAL/WARNING
        if priority in ["HIGH", "MEDIUM", "LOW"]:
            priority = "WARNING"

        result = await self.client.create_nrql_condition(
            account_id,
            policy_id,
            name,
            nrql_query,
            threshold,
            threshold_duration,
            threshold_operator,
            priority,
            aggregation_window,
            description,
        )

        if "error" in result:
            return self._create_error_response(f"creating NRQL condition '{name}': {result['error']}")

        condition_id = result.get("id", "Unknown")
        return self._create_success_response(
            f"NRQL alert condition '{name}' created successfully!\n"
            f"Condition ID: {condition_id}\nPolicy ID: {policy_id}\n"
            f"Threshold: {threshold_operator} {threshold} for {threshold_duration}s"
        )


class CreateNotificationDestinationHandler(ToolHandlerStrategy):
    """Handler for creating notification destinations"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        name = arguments["name"]
        destination_type = arguments["type"]
        properties = arguments["properties"]

        result = await self.client.create_notification_destination(account_id, name, destination_type, properties)

        if "error" in result:
            return self._create_error_response(f"creating notification destination '{name}': {result['error']}")

        destination_id = result.get("id", "Unknown")
        return self._create_success_response(
            f"Notification destination '{name}' ({destination_type}) created successfully!\n"
            f"Destination ID: {destination_id}"
        )


class CreateNotificationChannelHandler(ToolHandlerStrategy):
    """Handler for creating notification channels"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        name = arguments["name"]
        destination_id = arguments["destination_id"]
        channel_type = arguments["type"]
        product = arguments.get("product", "IINT")
        properties = arguments.get("properties", {})

        result = await self.client.create_notification_channel(
            account_id, name, destination_id, channel_type, product, properties
        )

        if "error" in result:
            return self._create_error_response(f"creating notification channel '{name}': {result['error']}")

        channel_id = result.get("id", "Unknown")
        return self._create_success_response(
            f"Notification channel '{name}' ({channel_type}) created successfully!\n"
            f"Channel ID: {channel_id}\nDestination ID: {destination_id}"
        )


class CreateWorkflowHandler(ToolHandlerStrategy):
    """Handler for creating workflows"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        name = arguments["name"]
        channel_ids = arguments["channel_ids"]
        enabled = arguments.get("enabled", True)
        filter_name = arguments.get("filter_name", "Filter-name")
        filter_predicates = arguments.get("filter_predicates", [])

        result = await self.client.create_workflow(
            account_id, name, channel_ids, enabled, filter_name, filter_predicates
        )

        if "error" in result:
            return self._create_error_response(f"creating workflow '{name}': {result['error']}")

        workflow_id = result.get("id", "Unknown")
        return self._create_success_response(
            f"Workflow '{name}' created successfully!\nWorkflow ID: {workflow_id}\n"
            f"Connected to {len(channel_ids)} notification channel(s)"
        )


class ListAlertPoliciesHandler(ToolHandlerStrategy):
    """Handler for listing alert policies"""

    async def handle(self, _arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        policies = await self.client.list_alert_policies(account_id)

        if "error" in policies:
            return self._create_error_response(f"listing alert policies: {policies['error']}")

        policy_list = policies.get("policies", [])

        if not policy_list:
            return self._create_success_response("No alert policies found.")

        policies_text = f"Found {len(policy_list)} alert policies:\n\n"
        for policy in policy_list:
            name = policy.get("name", "Unknown")
            policy_id = policy.get("id", "Unknown")
            incident_preference = policy.get("incidentPreference", "Unknown")

            policies_text += f"- **{name}**\n"
            policies_text += f"  ID: {policy_id}\n"
            policies_text += f"  Incident Preference: {incident_preference}\n\n"

        return self._create_success_response(policies_text)


class ListAlertConditionsHandler(ToolHandlerStrategy):
    """Handler for listing alert conditions"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        policy_id = arguments.get("policy_id")

        conditions = await self.client.list_alert_conditions(account_id, policy_id)

        if "error" in conditions:
            return self._create_error_response(f"listing alert conditions: {conditions['error']}")

        condition_list = conditions.get("conditions", [])

        if not condition_list:
            scope = f" for policy {policy_id}" if policy_id else ""
            return self._create_success_response(f"No alert conditions found{scope}.")

        scope = f" for policy {policy_id}" if policy_id else ""
        conditions_text = f"Found {len(condition_list)} alert conditions{scope}:\n\n"

        for condition in condition_list:
            name = condition.get("name", "Unknown")
            condition_id = condition.get("id", "Unknown")
            enabled = condition.get("enabled", "Unknown")
            policy_name = condition.get("policyName", "Unknown")

            conditions_text += f"- **{name}**\n"
            conditions_text += f"  ID: {condition_id}\n"
            conditions_text += f"  Policy: {policy_name}\n"
            conditions_text += f"  Enabled: {enabled}\n\n"

        return self._create_success_response(conditions_text)


class ListNotificationDestinationsHandler(ToolHandlerStrategy):
    """Handler for listing notification destinations"""

    async def handle(self, _arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        destinations = await self.client.list_notification_destinations(account_id)

        if "error" in destinations:
            return self._create_error_response(f"listing notification destinations: {destinations['error']}")

        destination_list = destinations.get("destinations", [])

        if not destination_list:
            return self._create_success_response("No notification destinations found.")

        destinations_text = f"Found {len(destination_list)} notification destinations:\n\n"
        for dest in destination_list:
            name = dest.get("name", "Unknown")
            dest_id = dest.get("id", "Unknown")
            dest_type = dest.get("type", "Unknown")

            destinations_text += f"- **{name}**\n"
            destinations_text += f"  ID: {dest_id}\n"
            destinations_text += f"  Type: {dest_type}\n\n"

        return self._create_success_response(destinations_text)


class ListNotificationChannelsHandler(ToolHandlerStrategy):
    """Handler for listing notification channels"""

    async def handle(self, _arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        channels = await self.client.list_notification_channels(account_id)

        if "error" in channels:
            return self._create_error_response(f"listing notification channels: {channels['error']}")

        channel_list = channels.get("channels", [])

        if not channel_list:
            return self._create_success_response("No notification channels found.")

        channels_text = f"Found {len(channel_list)} notification channels:\n\n"
        for channel in channel_list:
            name = channel.get("name", "Unknown")
            channel_id = channel.get("id", "Unknown")
            channel_type = channel.get("type", "Unknown")
            destination_id = channel.get("destinationId", "Unknown")

            channels_text += f"- **{name}**\n"
            channels_text += f"  ID: {channel_id}\n"
            channels_text += f"  Type: {channel_type}\n"
            channels_text += f"  Destination ID: {destination_id}\n\n"

        return self._create_success_response(channels_text)


class ListWorkflowsHandler(ToolHandlerStrategy):
    """Handler for listing workflows"""

    async def handle(self, _arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        workflows = await self.client.list_workflows(account_id)

        if "error" in workflows:
            return self._create_error_response(f"listing workflows: {workflows['error']}")

        workflow_list = workflows.get("workflows", [])

        if not workflow_list:
            return self._create_success_response("No workflows found.")

        workflows_text = f"Found {len(workflow_list)} workflows:\n\n"
        for workflow in workflow_list:
            name = workflow.get("name", "Unknown")
            workflow_id = workflow.get("id", "Unknown")

            workflows_text += f"- **{name}**\n"
            workflows_text += f"  ID: {workflow_id}\n\n"

        return self._create_success_response(workflows_text)
