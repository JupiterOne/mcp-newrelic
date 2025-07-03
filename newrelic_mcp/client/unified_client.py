"""
Unified New Relic client combining all functionality.
"""

from .alerts_client import AlertsClient
from .dashboards_client import DashboardsClient
from .monitoring_client import MonitoringClient


class NewRelicClient(MonitoringClient, AlertsClient, DashboardsClient):
    """Unified New Relic client combining all functionality"""

    pass
