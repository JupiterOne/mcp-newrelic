"""
New Relic Monitoring API client.

Handles applications, performance metrics, error tracking, and infrastructure monitoring.
"""

import logging
from typing import Any

from .base_client import BaseNewRelicClient

logger = logging.getLogger(__name__)


class MonitoringClient(BaseNewRelicClient):
    """Client for New Relic monitoring APIs"""

    async def get_applications(self, account_id: str) -> list[dict[str, Any]]:
        """Get list of applications"""
        query = "SELECT uniques(appName) as 'applications' FROM Transaction SINCE 1 day ago LIMIT 100"
        result = await self.query_nrql(account_id, query)

        nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
        if not nrql_results:
            logger.warning("No applications found in NRQL results")
            return []

        # Extract application names from the results
        apps = []
        for item in nrql_results:
            if "applications" in item and item["applications"]:
                for app_name in item["applications"]:
                    apps.append({"name": app_name, "appName": app_name})

        return apps

    async def get_recent_incidents(self, account_id: str, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent incidents"""
        # Use a more general query for incidents/alerts
        query = f"SELECT * FROM NrAiIncident SINCE {hours} hours ago LIMIT 50"
        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            return nrql_results if nrql_results else []
        except Exception as e:
            logger.warning(f"Incident query failed, trying alternative: {e}")
            # Fallback to alert violations
            query = f"SELECT * FROM Alert SINCE {hours} hours ago LIMIT 50"
            try:
                result = await self.query_nrql(account_id, query)
                return result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            except Exception:
                logger.warning("Both incident queries failed, returning empty list")
                return []

    async def get_error_metrics(self, account_id: str, app_name: str, hours: int = 1) -> dict[str, Any]:
        """Get error metrics for an application"""
        query = f"SELECT count(*) as error_count, average(duration) as avg_duration FROM TransactionError WHERE appName = '{app_name}' SINCE {hours} hours ago"
        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])

            if nrql_results:
                return nrql_results[0]
            else:
                # Fallback query
                query = f"SELECT count(*) as error_count FROM Transaction WHERE appName = '{app_name}' AND error IS TRUE SINCE {hours} hours ago"
                result = await self.query_nrql(account_id, query)
                nrql_results = (
                    result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
                )
                return nrql_results[0] if nrql_results else {"error_count": 0, "avg_duration": None}

        except Exception as e:
            logger.error(f"Error metrics query failed: {e}")
            return {"error_count": "Unknown", "avg_duration": "Unknown", "error": str(e)}

    async def get_performance_metrics(self, account_id: str, app_name: str, hours: int = 1) -> dict[str, Any]:
        """Get performance metrics for an application"""
        query = f"SELECT average(duration) as avg_duration, percentile(duration, 95) as p95_duration, rate(count(*), 1 minute) as throughput FROM Transaction WHERE appName = '{app_name}' SINCE {hours} hours ago"
        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])

            if nrql_results:
                return nrql_results[0]
            else:
                logger.warning(f"No performance data found for app: {app_name}")
                return {"avg_duration": "No data", "p95_duration": "No data", "throughput": "No data"}

        except Exception as e:
            logger.error(f"Performance metrics query failed: {e}")
            return {"avg_duration": "Unknown", "p95_duration": "Unknown", "throughput": "Unknown", "error": str(e)}

    async def get_infrastructure_hosts(self, account_id: str, hours: int = 1) -> list[dict[str, Any]]:
        """Get infrastructure hosts and their metrics"""
        query = f"SELECT latest(cpuPercent) as cpu_percent, latest(memoryUsedPercent) as memory_percent, latest(diskUsedPercent) as disk_percent FROM SystemSample FACET hostname SINCE {hours} hours ago LIMIT 50"
        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            return nrql_results if nrql_results else []
        except Exception as e:
            logger.error(f"Infrastructure hosts query failed: {e}")
            # Fallback to simpler query
            try:
                query = f"SELECT uniques(hostname) as hosts FROM SystemSample SINCE {hours} hours ago LIMIT 50"
                result = await self.query_nrql(account_id, query)
                nrql_results = (
                    result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
                )
                return nrql_results if nrql_results else []
            except Exception:
                logger.warning("Infrastructure hosts query failed completely")
                return []

    async def get_alert_violations(self, account_id: str, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent alert violations"""
        query = f"SELECT * FROM NrAiIncident WHERE state IN ('ACTIVATED', 'CLOSED') SINCE {hours} hours ago LIMIT 50"
        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            return nrql_results if nrql_results else []
        except Exception as e:
            logger.warning(f"Alert violations query failed, trying alternative: {e}")
            # Fallback to alert events
            try:
                query = f"SELECT * FROM AlertEvent SINCE {hours} hours ago LIMIT 50"
                result = await self.query_nrql(account_id, query)
                return result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            except Exception:
                logger.warning("Both alert violation queries failed, returning empty list")
                return []

    async def get_deployments(
        self, account_id: str, app_name: str | None = None, hours: int = 168
    ) -> list[dict[str, Any]]:
        """Get deployment markers and their impact"""
        if app_name:
            query = f"SELECT * FROM Deployment WHERE appName = '{app_name}' SINCE {hours} hours ago LIMIT 20"
        else:
            query = f"SELECT * FROM Deployment SINCE {hours} hours ago LIMIT 50"

        try:
            result = await self.query_nrql(account_id, query)
            nrql_results = result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            return nrql_results if nrql_results else []
        except Exception as e:
            logger.warning(f"Deployments query failed, trying alternative: {e}")
            # Fallback to transaction data with deployment correlation
            try:
                if app_name:
                    query = f"SELECT count(*) as transaction_count, average(duration) as avg_duration FROM Transaction WHERE appName = '{app_name}' FACET timestamp SINCE {hours} hours ago LIMIT 20"
                else:
                    query = f"SELECT count(*) as transaction_count, average(duration) as avg_duration FROM Transaction FACET appName SINCE {hours} hours ago LIMIT 20"

                result = await self.query_nrql(account_id, query)
                return result.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            except Exception:
                logger.warning("Deployments fallback query failed, returning empty list")
                return []
