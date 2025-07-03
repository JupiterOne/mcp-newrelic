"""
New Relic Alerts API client.

Handles alert policies, conditions, destinations, channels, and workflows.
"""

import logging
from typing import Any

from ..utils.error_handling import handle_api_error, handle_graphql_notification_errors
from ..utils.graphql_helpers import (
    extract_alert_data,
    extract_notification_data,
    extract_workflow_data,
)
from ..utils.response_formatters import format_create_response
from .base_client import BaseNewRelicClient

logger = logging.getLogger(__name__)


class AlertsClient(BaseNewRelicClient):
    """Client for New Relic alerts APIs"""

    async def create_alert_policy(
        self, account_id: str, name: str, incident_preference: str = "PER_POLICY"
    ) -> dict[str, Any]:
        """Create a new alert policy"""
        mutation = """
        mutation($accountId: Int!, $policy: AlertsPolicyInput!) {
          alertsPolicyCreate(accountId: $accountId, policy: $policy) {
            id
            name
            incidentPreference
          }
        }
        """

        policy_input = {"name": name, "incidentPreference": incident_preference}

        try:
            result = await self.execute_graphql(mutation, {"accountId": int(account_id), "policy": policy_input})

            policy_result = result.get("data", {}).get("alertsPolicyCreate", {})
            if not policy_result:
                return {"error": "Failed to create alert policy"}

            return format_create_response(
                policy_result,
                policy_id="id",
                name="name",
                incident_preference="incidentPreference"
            )

        except Exception as e:
            return handle_api_error("create alert policy", e)

    async def create_nrql_condition(
        self,
        account_id: str,
        policy_id: str,
        name: str,
        nrql_query: str,
        threshold: float,
        threshold_duration: int = 300,
        threshold_operator: str = "ABOVE",
        priority: str = "CRITICAL",
        aggregation_window: int = 60,
        description: str = None,
    ) -> dict[str, Any]:
        """Create a NRQL alert condition"""
        mutation = """
        mutation($accountId: Int!, $policyId: ID!, $condition: AlertsNrqlConditionStaticInput!) {
          alertsNrqlConditionStaticCreate(accountId: $accountId, policyId: $policyId, condition: $condition) {
            id
            name
            enabled
            nrql {
              query
            }
            signal {
              aggregationWindow
              evaluationOffset
            }
            terms {
              operator
              priority
              threshold
              thresholdDuration
              thresholdOccurrences
            }
          }
        }
        """

        condition_config = {
            "name": name,
            "enabled": True,
            "nrql": {"query": nrql_query},
            "signal": {"aggregationWindow": aggregation_window, "evaluationOffset": 3},
            "terms": [
                {
                    "operator": threshold_operator,
                    "priority": priority,
                    "threshold": threshold,
                    "thresholdDuration": threshold_duration,
                    "thresholdOccurrences": "AT_LEAST_ONCE",
                }
            ],
        }

        if description:
            condition_config["description"] = description

        try:
            result = await self.execute_graphql(
                mutation, {"accountId": int(account_id), "policyId": policy_id, "condition": condition_config}
            )

            condition_result = result.get("data", {}).get("alertsNrqlConditionStaticCreate", {})
            if not condition_result:
                return {"error": "Failed to create NRQL condition"}

            return format_create_response(
                condition_result,
                condition_id="id",
                name="name",
                enabled="enabled",
                query=["nrql", "query"],
                terms="terms"
            )

        except Exception as e:
            return handle_api_error("create NRQL condition", e)

    async def create_notification_destination(
        self, account_id: str, name: str, destination_type: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a notification destination"""
        mutation = """
        mutation($accountId: Int!, $destination: AiNotificationsDestinationInput!) {
          aiNotificationsCreateDestination(accountId: $accountId, destination: $destination) {
            destination {
              id
              name
              type
              properties {
                key
                value
              }
            }
            errors {
              __typename
              ... on AiNotificationsResponseError {
                description
                type
              }
              ... on AiNotificationsSuggestionError {
                description
                type
              }
            }
          }
        }
        """

        destination_config = {
            "name": name,
            "type": destination_type,
            "properties": [{"key": k, "value": v} for k, v in properties.items()],
        }

        try:
            result = await self.execute_graphql(
                mutation, {"accountId": int(account_id), "destination": destination_config}
            )

            create_result = result.get("data", {}).get("aiNotificationsCreateDestination", {})
            error_response = handle_graphql_notification_errors(create_result, "Destination creation")
            if error_response:
                return error_response

            destination = create_result.get("destination", {})
            return format_create_response(
                destination,
                destination_id="id",
                name="name",
                type="type",
                properties="properties"
            )

        except Exception as e:
            return handle_api_error("create notification destination", e)

    async def create_notification_channel(
        self,
        account_id: str,
        name: str,
        destination_id: str,
        channel_type: str,
        product: str = "IINT",
        properties: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Create a notification channel"""
        mutation = """
        mutation($accountId: Int!, $channel: AiNotificationsChannelInput!) {
          aiNotificationsCreateChannel(accountId: $accountId, channel: $channel) {
            channel {
              id
              name
              type
              destinationId
              product
              properties {
                key
                value
              }
            }
            errors {
              __typename
              ... on AiNotificationsResponseError {
                description
                type
              }
              ... on AiNotificationsSuggestionError {
                description
                type
              }
            }
          }
        }
        """

        channel_config = {
            "name": name,
            "type": channel_type,
            "destinationId": destination_id,
            "product": product,
            "properties": [{"key": k, "value": v} for k, v in (properties or {}).items()],
        }

        try:
            result = await self.execute_graphql(mutation, {"accountId": int(account_id), "channel": channel_config})

            create_result = result.get("data", {}).get("aiNotificationsCreateChannel", {})
            error_response = handle_graphql_notification_errors(create_result, "Channel creation")
            if error_response:
                return error_response

            channel = create_result.get("channel", {})
            return format_create_response(
                channel,
                channel_id="id",
                name="name",
                type="type",
                destination_id="destinationId",
                product="product",
                properties="properties"
            )

        except Exception as e:
            return handle_api_error("create notification channel", e)

    async def create_workflow(
        self,
        account_id: str,
        name: str,
        channel_ids: list[str],
        enabled: bool = True,
        filter_name: str = "Filter-name",
        filter_predicates: list[dict] = None,
    ) -> dict[str, Any]:
        """Create a workflow to connect alerts to notification channels"""
        mutation = """
        mutation($accountId: Int!, $createWorkflowData: AiWorkflowsCreateWorkflowInput!) {
          aiWorkflowsCreateWorkflow(accountId: $accountId, createWorkflowData: $createWorkflowData) {
            workflow {
              id
              name
              enrichments {
                configurations {
                  ... on AiWorkflowsNrqlConfiguration {
                    query
                  }
                }
                id
                name
                type
              }
              destinationConfigurations {
                channelId
                name
                type
              }
              issuesFilter {
                name
                predicates {
                  attribute
                  operator
                  values
                }
                type
              }
            }
            errors {
              __typename
              ... on AiNotificationsResponseError {
                description
                type
              }
              ... on AiNotificationsSuggestionError {
                description
                type
              }
            }
          }
        }
        """

        workflow_config = {
            "name": name,
            "enabled": enabled,
            "destinationConfigurations": [{"channelId": cid} for cid in channel_ids],
            "issuesFilter": {"name": filter_name, "type": "FILTER", "predicates": filter_predicates or []},
        }

        try:
            result = await self.execute_graphql(
                mutation, {"accountId": int(account_id), "createWorkflowData": workflow_config}
            )

            create_result = result.get("data", {}).get("aiWorkflowsCreateWorkflow", {})
            if create_result.get("errors"):
                return {"error": f"Workflow creation failed: {create_result['errors']}"}

            workflow = create_result.get("workflow", {})
            return format_create_response(
                workflow,
                workflow_id="id",
                name="name",
                destination_configurations="destinationConfigurations",
                issues_filter="issuesFilter",
                enrichments="enrichments"
            )

        except Exception as e:
            return handle_api_error("create workflow", e)

    async def get_alert_policies(self, account_id: str) -> dict[str, Any]:
        """Get list of alert policies"""
        query = f"""
        query {{
          actor {{
            account(id: {account_id}) {{
              alerts {{
                policiesSearch {{
                  policies {{
                    id
                    name
                    incidentPreference
                  }}
                  nextCursor
                  totalCount
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = await self.execute_graphql(query)
            policies_data = extract_alert_data(result, "policiesSearch")
            return {
                "policies": policies_data.get("policies", []),
                "total_count": policies_data.get("totalCount", 0),
                "next_cursor": policies_data.get("nextCursor"),
            }

        except Exception as e:
            return handle_api_error("get alert policies", e)

    async def get_alert_conditions(self, account_id: str, policy_id: str = None) -> dict[str, Any]:
        """Get alert conditions, optionally filtered by policy"""
        if policy_id:
            query = f"""
            query {{
              actor {{
                account(id: {account_id}) {{
                  alerts {{
                    nrqlConditionsSearch(searchCriteria: {{policyId: "{policy_id}"}}) {{
                      nrqlConditions {{
                        id
                        name
                        description
                        enabled
                        type
                        policyId
                        nrql {{
                          query
                        }}
                        terms {{
                          operator
                          priority
                          threshold
                          thresholdDuration
                          thresholdOccurrences
                        }}
                        signal {{
                          aggregationWindow
                          evaluationOffset
                          fillOption
                        }}
                        createdAt
                        updatedAt
                      }}
                      nextCursor
                      totalCount
                    }}
                  }}
                }}
              }}
            }}
            """
        else:
            query = f"""
            query {{
              actor {{
                account(id: {account_id}) {{
                  alerts {{
                    nrqlConditionsSearch {{
                      nrqlConditions {{
                        id
                        name
                        description
                        enabled
                        type
                        policyId
                        nrql {{
                          query
                        }}
                        terms {{
                          operator
                          priority
                          threshold
                          thresholdDuration
                          thresholdOccurrences
                        }}
                        signal {{
                          aggregationWindow
                          evaluationOffset
                          fillOption
                        }}
                        createdAt
                        updatedAt
                      }}
                      nextCursor
                      totalCount
                    }}
                  }}
                }}
              }}
            }}
            """

        try:
            result = await self.execute_graphql(query)

            if policy_id:
                conditions_data = (
                    result.get("data", {})
                    .get("actor", {})
                    .get("account", {})
                    .get("alerts", {})
                    .get("nrqlConditionsSearch", {})
                )
                return {
                    "policy_id": policy_id,
                    "conditions": conditions_data.get("nrqlConditions", []),
                    "total_count": conditions_data.get("totalCount", 0),
                    "next_cursor": conditions_data.get("nextCursor"),
                }
            else:
                conditions_data = (
                    result.get("data", {})
                    .get("actor", {})
                    .get("account", {})
                    .get("alerts", {})
                    .get("nrqlConditionsSearch", {})
                )
                return {
                    "conditions": conditions_data.get("nrqlConditions", []),
                    "total_count": conditions_data.get("totalCount", 0),
                    "next_cursor": conditions_data.get("nextCursor"),
                }

        except Exception as e:
            logger.error(f"Failed to get alert conditions: {e}")
            return {"error": str(e)}

    async def get_destinations(self, account_id: str) -> dict[str, Any]:
        """Get notification destinations"""
        query = f"""
        query {{
          actor {{
            account(id: {account_id}) {{
              aiNotifications {{
                destinations {{
                  entities {{
                    id
                    name
                    type
                    properties {{
                      key
                      value
                    }}
                    createdAt
                    updatedAt
                  }}
                  nextCursor
                  totalCount
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = await self.execute_graphql(query)
            destinations_data = extract_notification_data(result, "destinations")
            return {
                "destinations": destinations_data.get("entities", []),
                "total_count": destinations_data.get("totalCount", 0),
                "next_cursor": destinations_data.get("nextCursor"),
            }

        except Exception as e:
            return handle_api_error("get destinations", e)

    async def get_notification_channels(self, account_id: str) -> dict[str, Any]:
        """Get notification channels"""
        query = f"""
        query {{
          actor {{
            account(id: {account_id}) {{
              aiNotifications {{
                channels {{
                  entities {{
                    id
                    name
                    type
                    destinationId
                    product
                    properties {{
                      key
                      value
                    }}
                    createdAt
                    updatedAt
                  }}
                  nextCursor
                  totalCount
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = await self.execute_graphql(query)
            channels_data = extract_notification_data(result, "channels")
            return {
                "channels": channels_data.get("entities", []),
                "total_count": channels_data.get("totalCount", 0),
                "next_cursor": channels_data.get("nextCursor"),
            }

        except Exception as e:
            return handle_api_error("get notification channels", e)

    async def get_workflows(self, account_id: str) -> dict[str, Any]:
        """Get workflows"""
        query = f"""
        query {{
          actor {{
            account(id: {account_id}) {{
              aiWorkflows {{
                workflows {{
                  entities {{
                    id
                    name
                    destinationConfigurations {{
                      channelId
                      name
                      type
                    }}
                    issuesFilter {{
                      name
                      type
                      predicates {{
                        attribute
                        operator
                        values
                      }}
                    }}
                    enrichments {{
                      id
                      name
                      type
                    }}
                    createdAt
                    updatedAt
                  }}
                  nextCursor
                  totalCount
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = await self.execute_graphql(query)
            workflows_data = extract_workflow_data(result)
            return {
                "workflows": workflows_data.get("entities", []),
                "total_count": workflows_data.get("totalCount", 0),
                "next_cursor": workflows_data.get("nextCursor"),
            }

        except Exception as e:
            return handle_api_error("get workflows", e)

    # Alias methods for compatibility with handlers
    async def list_alert_policies(self, account_id: str) -> dict[str, Any]:
        """List alert policies - alias for get_alert_policies"""
        return await self.get_alert_policies(account_id)

    async def list_alert_conditions(self, account_id: str, policy_id: str = None) -> dict[str, Any]:
        """List alert conditions - alias for get_alert_conditions"""
        return await self.get_alert_conditions(account_id, policy_id)

    async def list_notification_destinations(self, account_id: str) -> dict[str, Any]:
        """List notification destinations - alias for get_destinations"""
        return await self.get_destinations(account_id)

    async def list_notification_channels(self, account_id: str) -> dict[str, Any]:
        """List notification channels - alias for get_notification_channels"""
        return await self.get_notification_channels(account_id)

    async def list_workflows(self, account_id: str) -> dict[str, Any]:
        """List workflows - alias for get_workflows"""
        return await self.get_workflows(account_id)
