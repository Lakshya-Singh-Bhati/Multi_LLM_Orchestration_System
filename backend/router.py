"""
router.py
---------
Task Router — decides which LLM provider should handle a given subtask.

Routing rules (simple and readable):
  - Technical explanations  → Gemini  (strong at precise, structured answers)
  - Examples / summaries / creative writing → Groq  (fast, conversational)

The function is intentionally kept deterministic and side-effect-free so it
can be unit-tested without any network calls.
"""

import logging

logger = logging.getLogger(__name__)

# Mapping of task_type → LLM provider name
_ROUTING_TABLE: dict[str, str] = {
    "explanation": "gemini",
    "technical":   "gemini",
    "analysis":    "gemini",
    "example":     "groq",
    "summary":     "groq",
    "creative":    "groq",
    "use_case":    "groq",
}

# Default provider when task_type is unrecognised
_DEFAULT_PROVIDER = "groq"


def assign_model(task_type: str) -> str:
    """
    Return the LLM provider name for a given task type.

    Args:
        task_type: One of 'explanation', 'technical', 'analysis',
                   'example', 'summary', 'creative', 'use_case'.

    Returns:
        'gemini' or 'groq'
    """
    provider = _ROUTING_TABLE.get(task_type.lower().strip(), _DEFAULT_PROVIDER)
    logger.debug("Router: task_type='%s' → provider='%s'", task_type, provider)
    return provider


def get_routing_table() -> dict[str, str]:
    """Return a copy of the routing table (useful for UI display)."""
    return dict(_ROUTING_TABLE)
