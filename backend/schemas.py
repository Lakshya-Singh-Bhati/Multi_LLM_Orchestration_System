"""
schemas.py
----------
Pydantic models used for request validation and response serialisation.
All data flowing through the API is typed here.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Payload sent by the Streamlit frontend to POST /chat."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's question or prompt.",
        examples=["Explain Retrieval-Augmented Generation and give a real-world use case."],
    )


# ---------------------------------------------------------------------------
# Internal data models
# ---------------------------------------------------------------------------

class SubTask(BaseModel):
    """A single subtask produced by the Planner."""

    task_id: int = Field(..., description="Sequential identifier (1 or 2).")
    description: str = Field(..., description="What this subtask asks the LLM to do.")
    task_type: str = Field(
        ...,
        description="Category of the task: 'explanation' | 'example' | 'summary' | 'creative'.",
    )
    assigned_model: str = Field(
        ..., description="LLM that will handle this subtask: 'gemini' | 'groq'."
    )


class TaskResult(BaseModel):
    """The output produced by an LLM for a single subtask."""

    task_id: int
    description: str
    assigned_model: str
    response: str
    success: bool = True
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ChatResponse(BaseModel):
    """Full response returned from POST /chat."""

    original_query: str
    subtasks: list[SubTask]
    task_results: list[TaskResult]
    final_response: str
    success: bool = True
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response from GET /health."""

    status: str = "healthy"
