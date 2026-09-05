"""
providers/gemini.py
-------------------
Async wrapper around the Google Gemini API.
Uses the `google-generativeai` SDK directly for full async support.
"""

import asyncio
import logging
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from config import settings

logger = logging.getLogger(__name__)


async def call_gemini(task_description: str) -> tuple[str, Optional[str]]:
    """
    Send *task_description* to Google Gemini and return the response text.

    Args:
        task_description: The subtask prompt to send to Gemini.

    Returns:
        A tuple of (response_text, error_message).
        On success, error_message is None.
        On failure, response_text is an empty string and error_message describes the issue.
    """
    if not settings.GEMINI_API_KEY:
        msg = "GEMINI_API_KEY is not configured."
        logger.error(msg)
        return "", msg

    try:
        # Configure the SDK with the API key
        genai.configure(api_key=settings.GEMINI_API_KEY)

        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)

        # Run the synchronous SDK call in a thread pool to stay non-blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(
                task_description,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                ),
                request_options={"timeout": settings.REQUEST_TIMEOUT},
            ),
        )

        text = response.text.strip()
        if not text:
            return "", "Gemini returned an empty response."

        logger.info("Gemini: received %d characters.", len(text))
        return text, None

    except GoogleAPIError as exc:
        msg = f"Gemini API error: {exc.message}"
        logger.error(msg)
        return "", msg
    except asyncio.TimeoutError:
        msg = f"Gemini request timed out after {settings.REQUEST_TIMEOUT}s."
        logger.error(msg)
        return "", msg
    except Exception as exc:
        msg = f"Unexpected Gemini error: {exc}"
        logger.error(msg)
        return "", msg
