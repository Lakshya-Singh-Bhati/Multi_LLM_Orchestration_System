"""
planner.py
----------
Planner module — uses Google Gemini via LangChain to intelligently decompose
a user's query into exactly two meaningful subtasks, then routes each subtask
to the appropriate LLM provider via the router.

Workflow (LangGraph StateGraph):
    parse_query → split_tasks → route_tasks → END
"""

import json
import re
import logging
from typing import TypedDict, Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from config import settings
from schemas import SubTask
from router import assign_model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LangGraph state definition
# ---------------------------------------------------------------------------

class PlannerState(TypedDict):
    """Mutable state passed between LangGraph nodes."""

    original_query: str
    raw_plan: str                   # Raw JSON string returned by the LLM
    subtasks: list[SubTask]         # Parsed & routed subtasks
    error: str | None


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def parse_query(state: PlannerState) -> PlannerState:
    """
    Node 1 — Send the user query to Gemini and ask for a two-task JSON plan.
    The LLM returns a structured JSON array so we can parse it reliably.
    """
    query = state["original_query"]
    logger.info("Planner: parsing query → '%s'", query[:80])

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )

    prompt = f"""You are an AI task planner. Analyse the user's query and decompose it
into EXACTLY TWO logical subtasks that together fully address the query.

Rules:
- Subtask 1 should focus on the conceptual / technical explanation.
- Subtask 2 should focus on examples, use-cases, summaries, or creative content.
- Respond with ONLY a valid JSON array — no markdown fences, no extra text.

JSON schema for each item:
{{
  "task_id": <1 or 2>,
  "description": "<clear one-sentence task description>",
  "task_type": "<explanation | example | summary | creative>"
}}

User query: {query}

JSON:"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        # Strip accidental markdown fences if the model adds them
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.MULTILINE).strip()
        raw = re.sub(r"```$", "", raw, flags=re.MULTILINE).strip()
        state["raw_plan"] = raw
        logger.debug("Planner raw plan: %s", raw)
    except Exception as exc:
        logger.error("Planner LLM error: %s", exc)
        state["error"] = str(exc)
        state["raw_plan"] = ""

    return state


def split_tasks(state: PlannerState) -> PlannerState:
    """
    Node 2 — Parse the raw JSON plan into SubTask objects.
    Falls back to a sensible default split if parsing fails.
    """
    if state.get("error") or not state.get("raw_plan"):
        # Fallback: create two generic subtasks from the original query
        logger.warning("Planner falling back to default task split.")
        state["subtasks"] = _default_subtasks(state["original_query"])
        return state

    try:
        data = json.loads(state["raw_plan"])
        subtasks = []
        for item in data[:2]:  # take at most 2
            subtasks.append(
                SubTask(
                    task_id=item["task_id"],
                    description=item["description"],
                    task_type=item.get("task_type", "explanation"),
                    assigned_model="",  # will be filled by route_tasks
                )
            )
        # Ensure we always have exactly 2 subtasks
        if len(subtasks) < 2:
            subtasks.append(_default_subtasks(state["original_query"])[1])

        state["subtasks"] = subtasks
        state["error"] = None
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("Planner JSON parse error: %s", exc)
        state["subtasks"] = _default_subtasks(state["original_query"])

    return state


def route_tasks(state: PlannerState) -> PlannerState:
    """
    Node 3 — Assign an LLM provider to each subtask using the router module.
    """
    routed: list[SubTask] = []
    for task in state["subtasks"]:
        model = assign_model(task.task_type)
        routed.append(task.model_copy(update={"assigned_model": model}))
    state["subtasks"] = routed
    logger.info(
        "Planner routed tasks: %s",
        [(t.task_id, t.assigned_model) for t in routed],
    )
    return state


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _default_subtasks(query: str) -> list[SubTask]:
    """Fallback: generic two-task split when LLM planning fails."""
    return [
        SubTask(
            task_id=1,
            description=f"Provide a detailed technical explanation about: {query}",
            task_type="explanation",
            assigned_model="",
        ),
        SubTask(
            task_id=2,
            description=f"Give real-world examples and use cases related to: {query}",
            task_type="example",
            assigned_model="",
        ),
    ]


# ---------------------------------------------------------------------------
# Build the LangGraph workflow
# ---------------------------------------------------------------------------

def build_planner_graph() -> StateGraph:
    """Construct and compile the planner LangGraph."""
    graph = StateGraph(PlannerState)

    graph.add_node("parse_query", parse_query)
    graph.add_node("split_tasks", split_tasks)
    graph.add_node("route_tasks", route_tasks)

    graph.set_entry_point("parse_query")
    graph.add_edge("parse_query", "split_tasks")
    graph.add_edge("split_tasks", "route_tasks")
    graph.add_edge("route_tasks", END)

    return graph.compile()


# Compiled graph — reused across requests
_planner_graph = build_planner_graph()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def plan(query: str) -> list[SubTask]:
    """
    Decompose *query* into two routed subtasks.

    Args:
        query: The user's original question.

    Returns:
        A list of exactly two SubTask objects with assigned_model populated.
    """
    initial_state: PlannerState = {
        "original_query": query,
        "raw_plan": "",
        "subtasks": [],
        "error": None,
    }

    # LangGraph's compiled graph is synchronous; run it directly.
    result = _planner_graph.invoke(initial_state)
    return result["subtasks"]
