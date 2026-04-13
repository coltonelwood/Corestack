"""ABF Integrations — third-party service connectors.

All external service calls flow through the dispatcher.
Models and routers never call connectors directly.
"""

from abf_integrations.base import (
    BaseConnector,
    ConnectorConfig,
    ExecutionResult,
    IntegrationMode,
)
from abf_integrations.dispatcher import dispatch, dispatch_batch, get_connector, list_connectors

__all__ = [
    "BaseConnector",
    "ConnectorConfig",
    "ExecutionResult",
    "IntegrationMode",
    "dispatch",
    "dispatch_batch",
    "get_connector",
    "list_connectors",
]
