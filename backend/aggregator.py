"""
aggregator.py
-------------
Aggregator module — combines the individual LLM responses into a single,
well-structured Markdown document and generates a brief combined summary.

The aggregator uses Groq (fast inference) to write the combined answer so
that the final output feels cohesive rather than simply concatenated.
"""

import logging
from typing import Optional

from groq import AsyncGroq, APIError

from config import settings
from schemas import TaskResult

logger = logging.getLogger(__name__)


def _model_badge(model_name: str) -> str:
    """Return a small emoji badge for a model name."""
    badges = {"gemini": "🔷 Google Gemini", "groq": "⚡ Groq"}
    return badges.get(model_name.lower(), model_name.upper())


def build_markdown_report(
    original_query: str,
    results: list[TaskResult],
    combined_summary: str,
) -> str:
    """
    Format the orchestration output as a Markdown document.

    Args:
        original_query: The user's original question.
        results:        List of TaskResult objects (one per subtask).
        combined_summary: A synthetically generated combined answer.

    Returns:
        A Markdown-formatted string ready to render in Streamlit.
    """
    sections: list[str] = []

    sections.append(f"## 🧠 Orchestration Results\n\n**Query:** _{original_query}_\n")
    sections.append("---")

    for result in results:
        badge = _model_badge(result.assigned_model)
        sections.append(f"### Task {result.task_id} — {badge}")
        sections.append(f"**Subtask:** {result.description}\n")
        if result.success:
            sections.append(result.response)
        else:
            sections.append(f"> ⚠️ **Error:** {result.error}")
        sections.append("\n---")

    sections.append("### ✨ Combined Answer")
    sections.append(combined_summary)

    return "\n\n".join(sections)


async def generate_combined_summary(
    original_query: str,
    results: list[TaskResult],
) -> tuple[str, Optional[str]]:
    """
    Use Groq to synthesise the two subtask responses into one coherent answer.

    Args:
        original_query: The user's original question.
        results:        Completed task results.

    Returns:
        (summary_text, error_message) — error_message is None on success.
    """
    if not settings.GROQ_API_KEY:
        # If no Groq key, concatenate directly without synthesis
        fallback = "\n\n".join(
            f"**{r.description}**\n\n{r.response}"
            for r in results
            if r.success
        )
        return fallback, None

    parts = []
    for r in results:
        if r.success:
            parts.append(f"[Task {r.task_id} — {r.assigned_model}]\n{r.response}")

    combined_context = "\n\n".join(parts)

    synthesis_prompt = f"""You are a synthesis assistant. Below are two responses generated
by different AI models for sub-parts of a user's query.

Original query: {original_query}

--- RESPONSES ---
{combined_context}
--- END ---

Write a single, cohesive, well-structured answer in Markdown that integrates
both responses naturally. Do not just concatenate them. Keep it concise.
"""

    try:
        client = AsyncGroq(
            api_key=settings.GROQ_API_KEY,
            timeout=settings.REQUEST_TIMEOUT,
        )
        completion = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.5,
            max_tokens=1024,
        )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            return combined_context, "Aggregator returned empty synthesis."
        return text, None
    except APIError as exc:
        logger.warning("Aggregator synthesis error: %s", exc)
        return combined_context, str(exc)
    except Exception as exc:
        logger.warning("Aggregator unexpected error: %s", exc)
        return combined_context, str(exc)


async def aggregate(
    original_query: str,
    results: list[TaskResult],
) -> str:
    """
    Main entry point — aggregate task results into a final Markdown response.

    Args:
        original_query: The user's question.
        results:        List of completed TaskResult objects.

    Returns:
        A Markdown-formatted string containing per-task sections and a
        combined synthesis.
    """
    summary, err = await generate_combined_summary(original_query, results)
    if err:
        logger.warning("Aggregator synthesis warning: %s", err)

    return build_markdown_report(original_query, results, summary)
