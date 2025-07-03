"""Monitoring tool handlers using Strategy pattern"""

from typing import Any

from mcp.types import TextContent

from .base import ToolHandlerStrategy


class QueryNRQLHandler(ToolHandlerStrategy):
    """Handler for NRQL query execution"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        query = arguments["query"]
        result = await self.client.query_nrql(account_id, query)
        return [TextContent(type="text", text=f"NRQL Query Results:\n```json\n{result}\n```")]


class AppPerformanceHandler(ToolHandlerStrategy):
    """Handler for application performance metrics"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        app_name = arguments["app_name"]
        hours = arguments.get("hours", 1)
        metrics = await self.client.get_performance_metrics(account_id, app_name, hours)

        if "error" in metrics:
            return self._create_error_response(f"getting performance metrics for {app_name}: {metrics['error']}")

        formatted_metrics = self._format_performance_metrics(metrics, app_name, hours)
        return self._create_success_response(formatted_metrics)

    def _format_performance_metrics(self, metrics: dict[str, Any], app_name: str, hours: int) -> str:
        """Format performance metrics for display"""
        avg_duration = self._format_duration(metrics.get("avg_duration"))
        p95_duration = self._format_duration(metrics.get("p95_duration"))
        throughput = self._format_throughput(metrics.get("throughput"))

        return (
            f"Performance metrics for '{app_name}' (last {hours}h):\n"
            f"- Average response time: {avg_duration}\n"
            f"- 95th percentile: {p95_duration}\n"
            f"- Throughput: {throughput}"
        )

    @staticmethod
    def _format_duration(duration: Any) -> str:
        """Format duration with proper units"""
        return f"{duration:.2f}ms" if isinstance(duration, int | float) else "N/A"

    @staticmethod
    def _format_throughput(throughput: Any) -> str:
        """Format throughput with proper units"""
        return f"{throughput:.2f} req/min" if isinstance(throughput, int | float) else "N/A"


class AppErrorsHandler(ToolHandlerStrategy):
    """Handler for application error metrics"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        app_name = arguments["app_name"]
        hours = arguments.get("hours", 1)
        metrics = await self.client.get_error_metrics(account_id, app_name, hours)

        if "error" in metrics:
            return self._create_error_response(f"getting error metrics for {app_name}: {metrics['error']}")

        error_count = metrics.get("error_count", "N/A")
        avg_duration = self._format_duration(metrics.get("avg_duration"))

        return self._create_success_response(
            f"Error metrics for '{app_name}' (last {hours}h):\n"
            f"- Error count: {error_count}\n"
            f"- Average error duration: {avg_duration}"
        )

    @staticmethod
    def _format_duration(duration: Any) -> str:
        """Format duration with proper units"""
        return f"{duration:.2f}ms" if isinstance(duration, int | float) else "N/A"


class IncidentsHandler(ToolHandlerStrategy):
    """Handler for incidents retrieval"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        hours = arguments.get("hours", 24)
        incidents = await self.client.get_recent_incidents(account_id, hours)

        if not incidents:
            return self._create_success_response(f"No incidents found in the last {hours} hours.")

        incident_text = f"Found {len(incidents)} incidents in the last {hours} hours:\n\n"
        for incident in incidents:
            incident_text += (
                f"- **{incident.get('title', 'Unknown')}**\n"
                f"  State: {incident.get('state', 'Unknown')}\n"
                f"  Time: {incident.get('timestamp', 'Unknown')}\n\n"
            )

        return self._create_success_response(incident_text)


class InfrastructureHandler(ToolHandlerStrategy):
    """Handler for infrastructure hosts"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        hours = arguments.get("hours", 1)
        hosts = await self.client.get_infrastructure_hosts(account_id, hours)

        if not hosts:
            return self._create_success_response(f"No infrastructure hosts found in the last {hours} hours.")

        host_text = f"Found {len(hosts)} infrastructure hosts (last {hours}h):\n\n"
        for host in hosts:
            hostname = host.get("hostname", "Unknown")
            cpu = host.get("cpu_percent", "N/A")
            memory = host.get("memory_percent", "N/A")
            disk = host.get("disk_percent", "N/A")

            host_text += f"- **{hostname}**\n"
            if cpu != "N/A":
                host_text += f"  CPU: {cpu:.1f}%\n"
            if memory != "N/A":
                host_text += f"  Memory: {memory:.1f}%\n"
            if disk != "N/A":
                host_text += f"  Disk: {disk:.1f}%\n"
            host_text += "\n"

        return self._create_success_response(host_text)


class AlertViolationsHandler(ToolHandlerStrategy):
    """Handler for alert violations"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        hours = arguments.get("hours", 24)
        violations = await self.client.get_alert_violations(account_id, hours)

        if not violations:
            return self._create_success_response(f"No alert violations found in the last {hours} hours.")

        violation_text = f"Found {len(violations)} alert violations (last {hours}h):\n\n"
        for violation in violations:
            title = violation.get("title", violation.get("name", "Unknown Alert"))
            state = violation.get("state", "Unknown")
            timestamp = violation.get("timestamp", violation.get("createdAt", "Unknown"))
            priority = violation.get("priority", violation.get("priority_level", "Unknown"))

            violation_text += f"- **{title}**\n  State: {state}\n  Priority: {priority}\n  Time: {timestamp}\n\n"

        return self._create_success_response(violation_text)


class DeploymentsHandler(ToolHandlerStrategy):
    """Handler for deployments"""

    async def handle(self, arguments: dict[str, Any], account_id: str) -> list[TextContent]:
        app_name = arguments.get("app_name")
        hours = arguments.get("hours", 168)
        deployments = await self.client.get_deployments(account_id, app_name, hours)

        if not deployments:
            scope = f"for {app_name} " if app_name else ""
            return self._create_success_response(f"No deployments found {scope}in the last {hours} hours.")

        scope = f"for {app_name} " if app_name else ""
        deployment_text = f"Found {len(deployments)} deployments {scope}(last {hours}h):\n\n"

        for deployment in deployments:
            app = deployment.get("appName", "Unknown App")
            timestamp = deployment.get("timestamp", deployment.get("createdAt", "Unknown"))
            revision = deployment.get("revision", "Unknown")
            description = deployment.get("description", "")

            deployment_text += f"- **{app}**\n"
            deployment_text += f"  Time: {timestamp}\n"
            deployment_text += f"  Revision: {revision}\n"
            if description:
                deployment_text += f"  Description: {description}\n"
            deployment_text += "\n"

        return self._create_success_response(deployment_text)
