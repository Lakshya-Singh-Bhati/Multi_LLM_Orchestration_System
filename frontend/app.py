"""
app.py
------
Streamlit frontend for the Multi-LLM Orchestration Platform.

Features:
  - Modern dark chat interface with glassmorphism cards
  - Real-time pipeline visualisation
  - Per-task result display with model badges
  - Session-state-based chat history
  - Clear chat button
  - Error display with actionable messages
"""

import streamlit as st
import requests
import json

from components import render_chat_message, render_sidebar_info

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Multi-LLM Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS — dark premium theme
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Root & body ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0d0d1a 0%, #12122a 50%, #0d0d1a 100%);
        color: #e0e0f0;
    }

    /* ── Hide default Streamlit chrome ───────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Sidebar ─────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 40, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Chat input ──────────────────────────────────────────── */
    .stChatInput textarea {
        background: rgba(255,255,255,0.05) !important;
        color: #e0e0f0 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Expander styling ────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        font-weight: 600 !important;
    }

    /* ── Buttons ─────────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #7928ca, #ff0080) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(121,40,202,0.5) !important;
    }

    /* ── Divider ─────────────────────────────────────────────── */
    hr { border-color: rgba(255,255,255,0.08) !important; }

    /* ── Info / Error boxes ──────────────────────────────────── */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* ── Spinner ─────────────────────────────────────────────── */
    .stSpinner > div {
        border-top-color: #7928ca !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE}/chat"
HEALTH_ENDPOINT = f"{API_BASE}/health"

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history: list[dict] = []

if "api_healthy" not in st.session_state:
    st.session_state.api_healthy = False

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def check_api_health() -> bool:
    """Ping the backend health endpoint and return True if healthy."""
    try:
        resp = requests.get(HEALTH_ENDPOINT, timeout=5)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False


def send_chat_request(query: str) -> dict:
    """
    POST the user query to the backend and return the parsed JSON response.
    Raises requests.HTTPError on non-2xx responses.
    """
    resp = requests.post(
        CHAT_ENDPOINT,
        json={"query": query},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_sidebar_info()

# API health status in sidebar
with st.sidebar:
    st.divider()
    healthy = check_api_health()
    st.session_state.api_healthy = healthy
    if healthy:
        st.success("✅ API is online", icon="🟢")
    else:
        st.error("❌ API is offline — start the FastAPI server.", icon="🔴")

    if st.button("🔄 Refresh Status"):
        st.rerun()

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div style="text-align:center;padding:32px 0 8px;">
      <h1 style="
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7928ca, #ff0080, #4285F4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
      ">
        🤖 Multi-LLM Orchestration Platform
      </h1>
      <p style="color:#8888aa;font-size:1rem;margin:0;">
        Watch Gemini &amp; Groq collaborate in real time to answer your questions
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Render existing chat history
# ---------------------------------------------------------------------------

for message in st.session_state.chat_history:
    render_chat_message(
        role=message["role"],
        content=message["content"],
        metadata=message.get("metadata"),
    )

# ---------------------------------------------------------------------------
# Chat input — bottom of page
# ---------------------------------------------------------------------------

if prompt := st.chat_input(
    "Ask anything… e.g. 'Explain RAG and give a real-world use case'",
    disabled=not st.session_state.api_healthy,
):
    # Append user message to history and render it
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    render_chat_message("user", prompt)

    # Show progress while calling the backend
    with st.spinner("🧠 Orchestrating… Planner → Router → Gemini & Groq → Aggregator"):
        try:
            data = send_chat_request(prompt)

            subtasks = data.get("subtasks", [])
            task_results = data.get("task_results", [])
            final_response = data.get("final_response", "No response generated.")

            metadata = {
                "subtasks": subtasks,
                "task_results": task_results,
            }

            # Append assistant message
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": final_response,
                    "metadata": metadata,
                }
            )

            render_chat_message("assistant", final_response, metadata=metadata)

        except requests.exceptions.ConnectionError:
            st.error(
                "⚠️ Cannot connect to the FastAPI backend. "
                "Make sure it is running on http://localhost:8000"
            )
        except requests.exceptions.Timeout:
            st.error(
                "⏱️ The request timed out. The LLM providers may be slow. "
                "Please try again."
            )
        except requests.exceptions.HTTPError as exc:
            try:
                detail = exc.response.json().get("detail", str(exc))
            except Exception:
                detail = str(exc)
            st.error(f"❌ API error: {detail}")
        except Exception as exc:
            st.error(f"❌ Unexpected error: {exc}")
