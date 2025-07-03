"""
Base New Relic API client.

Provides common HTTP client functionality and NRQL query capabilities.
"""

import logging
from typing import Any

import httpx

from ..config import NewRelicConfig

logger = logging.getLogger(__name__)


class BaseNewRelicClient:
    """Base client for interacting with New Relic APIs"""

    def __init__(self, config: NewRelicConfig):
        self.config = config
        self.base_url = "https://api.newrelic.com" if config.region == "US" else "https://api.eu.newrelic.com"
        self.headers: dict[str, str] = {"Api-Key": config.api_key or "", "Content-Type": "application/json"}

    async def _execute_http_request(self, payload: dict[str, Any], operation_name: str = "GraphQL") -> dict[str, Any]:
        """Execute HTTP request with common error handling"""
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(f"{self.base_url}/graphql", headers=self.headers, json=payload)
                response.raise_for_status()
                result: dict[str, Any] = response.json()

                # Check for GraphQL errors
                if "errors" in result:
                    logger.error(f"GraphQL errors: {result['errors']}")
                    raise ValueError(f"GraphQL query failed: {result['errors']}")

                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"{operation_name} failed: {e}")
            raise

    async def query_nrql(self, account_id: str, query: str) -> dict[str, Any]:
        """Execute a NRQL query"""
        graphql_query = {
            "query": f"""
            query {{
                actor {{
                    account(id: {account_id}) {{
                        nrql(query: "{query}") {{
                            results
                        }}
                    }}
                }}
            }}
            """
        }

        logger.debug(f"Executing NRQL query: {query}")
        result = await self._execute_http_request(graphql_query, "NRQL Query")
        logger.debug(f"Query result: {result}")
        return result

    async def execute_graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query with optional variables"""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        return await self._execute_http_request(payload, "GraphQL execution")
