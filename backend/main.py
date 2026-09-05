"""
main.py
-------
FastAPI application entry-point.
Wires together the routes, CORS middleware, and startup validation.
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import router

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Validate configuration at startup
    config_errors = settings.validate()
    if config_errors:
        for err in config_errors:
            logger.warning("[WARN] Config warning: %s", err)

    app = FastAPI(
        title="Multi-LLM Orchestration Platform",
        description=(
            "An AI orchestration backend that decomposes a user query into subtasks "
            "and routes them concurrently to Google Gemini and Groq LLMs."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Allow the Streamlit frontend (any origin in dev) to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        logger.info("[START] Multi-LLM Orchestration API is starting up...")
        errors = settings.validate()
        if errors:
            logger.warning(
                "Some API keys are missing. Requests may fail: %s", errors
            )
        else:
            logger.info("[OK] All API keys configured.")

    return app


app = create_app()

# ---------------------------------------------------------------------------
# Dev server entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
