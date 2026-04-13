"""Agent registry — discover and instantiate agents by name."""

from __future__ import annotations

from abf_agents.base import BaseAgent

_registry: dict[str, type[BaseAgent]] = {}


def register(cls: type[BaseAgent]) -> type[BaseAgent]:
    """Class decorator to register an agent type."""
    _registry[cls.name] = cls
    return cls


def get_agent(name: str) -> BaseAgent:
    """Instantiate a registered agent by name."""
    cls = _registry.get(name)
    if cls is None:
        raise KeyError(f"Unknown agent: {name!r}. Available: {list(_registry)}")
    return cls()


def registry() -> dict[str, type[BaseAgent]]:
    """Return the current agent registry."""
    return dict(_registry)
