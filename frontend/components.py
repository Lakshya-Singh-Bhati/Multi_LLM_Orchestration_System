"""
components.py
-------------
Reusable Streamlit UI components for the Multi-LLM Orchestration Platform.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Colour & badge helpers
# ---------------------------------------------------------------------------

MODEL_COLOURS = {
    "gemini": "#4285F4",   # Google blue
    "groq":   "#F55036",   # Groq orange-red
}

MODEL_LABELS = {
    "gemini": "🔷 Google Gemini",
    "groq":   "⚡ Groq LLM",
}


def model_badge(model: str) -> str:
    """Return an HTML badge for the model name."""
    colour = MODEL_COLOURS.get(model, "#888")
    label = MODEL_LABELS.get(model, model.upper())
    return (
        f'<span style="background:{colour};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.8rem;font-weight:600;">{label}</span>'
    )


# ---------------------------------------------------------------------------
# Pipeline visualisation
# ---------------------------------------------------------------------------

def render_pipeline_diagram(subtasks: list[dict]) -> None:
    """Render the orchestration pipeline as a styled HTML card."""

    task1 = subtasks[0] if subtasks else {}
    task2 = subtasks[1] if len(subtasks) > 1 else {}

    m1 = task1.get("assigned_model", "gemini")
    m2 = task2.get("assigned_model", "groq")

    t1_label = MODEL_LABELS.get(m1, m1.upper())
    t2_label = MODEL_LABELS.get(m2, m2.upper())
    t1_colour = MODEL_COLOURS.get(m1, "#888")
    t2_colour = MODEL_COLOURS.get(m2, "#888")

    html = f"""
    <div style="
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 16px;
        padding: 28px 32px;
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
        margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    ">
      <h4 style="text-align:center;margin:0 0 20px;letter-spacing:2px;
                 font-size:0.85rem;color:#aaa;text-transform:uppercase;">
        🔄 Orchestration Pipeline
      </h4>

      <!-- User Query -->
      <div style="text-align:center;margin-bottom:12px;">
        <div style="display:inline-block;background:rgba(255,255,255,0.08);
                    border:1px solid rgba(255,255,255,0.15);border-radius:10px;
                    padding:10px 24px;font-weight:600;font-size:0.95rem;">
          👤 User Query
        </div>
      </div>

      <!-- Arrow down -->
      <div style="text-align:center;font-size:1.5rem;color:#7c7c9c;margin:4px 0;">↓</div>

      <!-- Planner -->
      <div style="text-align:center;margin-bottom:4px;">
        <div style="display:inline-block;background:linear-gradient(135deg,#7928ca,#ff0080);
                    border-radius:10px;padding:10px 28px;font-weight:700;font-size:0.95rem;
                    box-shadow:0 4px 15px rgba(121,40,202,0.4);">
          🧠 Planner (LangGraph)
        </div>
      </div>

      <div style="text-align:center;font-size:1.5rem;color:#7c7c9c;margin:4px 0;">↓</div>

      <!-- Task Splitter -->
      <div style="text-align:center;margin-bottom:12px;">
        <div style="display:inline-block;background:rgba(255,255,255,0.07);
                    border:1px dashed rgba(255,255,255,0.2);border-radius:10px;
                    padding:8px 22px;font-size:0.88rem;">
          ✂️ Task Splitter
        </div>
      </div>

      <!-- Parallel tasks -->
      <div style="display:flex;justify-content:center;gap:24px;margin-bottom:12px;">
        <!-- Task 1 -->
        <div style="flex:1;max-width:280px;">
          <div style="background:rgba(255,255,255,0.06);border-radius:10px;
                      padding:14px;border-left:4px solid {t1_colour};">
            <div style="font-size:0.75rem;color:#aaa;margin-bottom:6px;
                        text-transform:uppercase;letter-spacing:1px;">Task 1</div>
            <div style="font-size:0.85rem;line-height:1.4;">
              {task1.get('description', 'Technical explanation')[:80]}...
            </div>
          </div>
          <div style="text-align:center;font-size:1.2rem;color:#7c7c9c;margin:6px 0;">↓</div>
          <div style="text-align:center;">
            <div style="display:inline-block;background:{t1_colour};
                        border-radius:8px;padding:8px 18px;font-weight:700;
                        font-size:0.85rem;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
              {t1_label}
            </div>
          </div>
        </div>

        <!-- Divider -->
        <div style="width:1px;background:rgba(255,255,255,0.12);margin:0 8px;"></div>

        <!-- Task 2 -->
        <div style="flex:1;max-width:280px;">
          <div style="background:rgba(255,255,255,0.06);border-radius:10px;
                      padding:14px;border-left:4px solid {t2_colour};">
            <div style="font-size:0.75rem;color:#aaa;margin-bottom:6px;
                        text-transform:uppercase;letter-spacing:1px;">Task 2</div>
            <div style="font-size:0.85rem;line-height:1.4;">
              {task2.get('description', 'Examples & use cases')[:80]}...
            </div>
          </div>
          <div style="text-align:center;font-size:1.2rem;color:#7c7c9c;margin:6px 0;">↓</div>
          <div style="text-align:center;">
            <div style="display:inline-block;background:{t2_colour};
                        border-radius:8px;padding:8px 18px;font-weight:700;
                        font-size:0.85rem;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
              {t2_label}
            </div>
          </div>
        </div>
      </div>

      <div style="text-align:center;font-size:1.5rem;color:#7c7c9c;margin:4px 0;">↓</div>

      <!-- Aggregator -->
      <div style="text-align:center;margin-bottom:4px;">
        <div style="display:inline-block;
                    background:linear-gradient(135deg,#11998e,#38ef7d);
                    border-radius:10px;padding:10px 28px;font-weight:700;
                    color:#111;font-size:0.95rem;
                    box-shadow:0 4px 15px rgba(56,239,125,0.3);">
          🔗 Aggregator
        </div>
      </div>

      <div style="text-align:center;font-size:1.5rem;color:#7c7c9c;margin:4px 0;">↓</div>

      <!-- Final Response -->
      <div style="text-align:center;">
        <div style="display:inline-block;background:rgba(255,255,255,0.08);
                    border:1px solid rgba(255,255,255,0.15);border-radius:10px;
                    padding:10px 24px;font-weight:600;font-size:0.95rem;">
          ✨ Final Response
        </div>
      </div>
    </div>
    """
    st.html(html)


# ---------------------------------------------------------------------------
# Task cards
# ---------------------------------------------------------------------------

def render_task_card(task_result: dict) -> None:
    """Render a collapsible card for a single task result."""
    model = task_result.get("assigned_model", "unknown")
    colour = MODEL_COLOURS.get(model, "#888")
    label = MODEL_LABELS.get(model, model.upper())
    task_id = task_result.get("task_id", "?")
    description = task_result.get("description", "")
    success = task_result.get("success", True)
    response = task_result.get("response", "")
    error = task_result.get("error")

    icon = "✅" if success else "❌"

    with st.expander(
        f"{icon} Task {task_id} → {label}",
        expanded=True,
    ):
        st.markdown(
            f'<div style="margin-bottom:8px;">'
            f'<strong>Subtask:</strong> {description}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="margin-bottom:12px;">'
            f'<strong>Model:</strong> '
            + model_badge(model) +
            f'</div>',
            unsafe_allow_html=True,
        )
        if success:
            st.markdown(response)
        else:
            st.error(f"⚠️ {error}")


# ---------------------------------------------------------------------------
# Sidebar info
# ---------------------------------------------------------------------------

def render_sidebar_info() -> None:
    """Render project info and routing rules in the sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:16px 0 8px;">
              <div style="font-size:2.2rem;">🤖</div>
              <h2 style="margin:4px 0;font-size:1.1rem;font-weight:700;">
                Multi-LLM Orchestrator
              </h2>
              <div style="font-size:0.78rem;color:#aaa;">
                Powered by Gemini + Groq
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("#### 🔀 Routing Rules")
        st.markdown(
            """
            | Task Type | Provider |
            |---|---|
            | Explanation | 🔷 Gemini |
            | Technical | 🔷 Gemini |
            | Analysis | 🔷 Gemini |
            | Example | ⚡ Groq |
            | Summary | ⚡ Groq |
            | Creative | ⚡ Groq |
            """
        )

        st.divider()

        st.markdown("#### ⚙️ Architecture")
        st.markdown(
            """
            1. **Planner** — LangGraph workflow decomposes the query
            2. **Router** — maps task type → LLM
            3. **Concurrent** — `asyncio.gather()` runs both LLMs simultaneously
            4. **Aggregator** — Groq synthesises the final answer
            """
        )

        st.divider()
        st.caption("Built with FastAPI · Streamlit · LangGraph")


# ---------------------------------------------------------------------------
# Chat message renderer
# ---------------------------------------------------------------------------

def render_chat_message(role: str, content: str, metadata: dict | None = None) -> None:
    """
    Render a single chat message bubble.

    Args:
        role: 'user' or 'assistant'
        content: The message text (Markdown supported for assistant).
        metadata: Optional dict with orchestration details.
    """
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            if metadata and metadata.get("subtasks"):
                st.markdown("---")
                render_pipeline_diagram(metadata["subtasks"])

                if metadata.get("task_results"):
                    st.markdown("#### 📋 Individual Task Results")
                    for tr in metadata["task_results"]:
                        render_task_card(tr)

                st.markdown("---")
                st.markdown("#### ✨ Final Combined Answer")

            st.markdown(content)
