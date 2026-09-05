"""
routes.py
---------
FastAPI route definitions.
Separates routing logic from the application entry-point (main.py).
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException

from schemas import ChatRequest, ChatResponse, HealthResponse, TaskResult
from planner import plan
from providers import call_gemini, call_groq
from aggregator import aggregate

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Returns a simple health status so the frontend can verify the API is up."""
    return HealthResponse(status="healthy")


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse, tags=["Orchestration"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main orchestration endpoint.

    Pipeline:
        1. Planner decomposes the query into two subtasks.
        2. Router assigns each subtask to a provider (gemini / groq).
        3. Both providers are called concurrently with asyncio.gather().
        4. Aggregator merges the responses into a final Markdown answer.
    """
    query = request.query.strip()
    logger.info("Received query: '%s'", query[:80])

    # ---- Step 1: Plan -------------------------------------------------
    try:
        subtasks = await plan(query)
    except Exception as exc:
        logger.error("Planner error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Planner error: {exc}") from exc

    # ---- Step 2 & 3: Route + Execute concurrently ----------------------
    async def execute_task(task) -> TaskResult:
        """Call the appropriate provider for a single subtask."""
        try:
            if task.assigned_model == "gemini":
                text, error = await call_gemini(task.description)
            else:
                text, error = await call_groq(task.description)

            if error:
                return TaskResult(
                    task_id=task.task_id,
                    description=task.description,
                    assigned_model=task.assigned_model,
                    response="",
                    success=False,
                    error=error,
                )
            return TaskResult(
                task_id=task.task_id,
                description=task.description,
                assigned_model=task.assigned_model,
                response=text,
                success=True,
            )
        except Exception as exc:
            logger.error("Task %d execution error: %s", task.task_id, exc)
            return TaskResult(
                task_id=task.task_id,
                description=task.description,
                assigned_model=task.assigned_model,
                response="",
                success=False,
                error=str(exc),
            )

    # Concurrent execution
    results: list[TaskResult] = list(
        await asyncio.gather(*(execute_task(t) for t in subtasks))
    )

    # ---- Step 4: Aggregate --------------------------------------------
    try:
        final_response = await aggregate(query, results)
    except Exception as exc:
        logger.error("Aggregator error: %s", exc)
        final_response = "\n\n".join(
            r.response for r in results if r.success
        ) or "No response generated."

    return ChatResponse(
        original_query=query,
        subtasks=subtasks,
        task_results=results,
        final_response=final_response,
        success=True,
    )
