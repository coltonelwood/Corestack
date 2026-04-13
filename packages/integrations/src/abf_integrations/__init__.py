"""ABF Integrations — third-party service connectors.

All external service calls flow through connector classes.
Models and routers never call external APIs directly.
"""

from abf_integrations.base import BaseConnector, ConnectorResult

__all__ = ["BaseConnector", "ConnectorResult"]
