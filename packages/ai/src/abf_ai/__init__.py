"""ABF AI — AI/ML models, prompt management, task routing, and memory."""

from abf_ai.providers import (
    complete,
    complete_with_fallback,
    check_provider_health,
    estimate_cost,
    Provider,
    CompletionResult,
    ProviderHealth,
)
from abf_ai.prompts import PromptTemplate
from abf_ai.router import route_ai_task, TaskResult, ROUTING_TABLE, SAMPLE_PAYLOADS
from abf_ai.schemas import TASK_SCHEMAS
from abf_ai.memory import (
    save as save_memory,
    recall as recall_memory,
    MemoryEntry,
    save_decision_outcome,
    save_campaign_pattern,
    save_approval_rejection,
    save_copy_angle,
    recall_relevant_decisions,
    recall_campaign_patterns,
    build_context_string,
)

__all__ = [
    "complete",
    "complete_with_fallback",
    "check_provider_health",
    "estimate_cost",
    "Provider",
    "CompletionResult",
    "ProviderHealth",
    "PromptTemplate",
    "route_ai_task",
    "TaskResult",
    "ROUTING_TABLE",
    "SAMPLE_PAYLOADS",
    "TASK_SCHEMAS",
    "save_memory",
    "recall_memory",
    "MemoryEntry",
    "save_decision_outcome",
    "save_campaign_pattern",
    "save_approval_rejection",
    "save_copy_angle",
    "recall_relevant_decisions",
    "recall_campaign_patterns",
    "build_context_string",
]
