"""
providers/groq.py
-----------------
Async wrapper around the Groq API using the official `groq` Python SDK.
"""

import logging
from typing import Optional

from groq import AsyncGroq, APIError, APITimeoutError, AuthenticationError

from config import settings

logger = logging.getLogger(__name__)


async def call_groq(task_description: str) -> tuple[str, Optional[str]]:
    """
    Send *task_description* to Groq and return the response text.

    Args:
        task_description: The subtask prompt to send to Groq.

    Returns:
        A tuple of (response_text, error_message).
        On success, error_message is None.
        On failure, response_text is an empty string and error_message describes the issue.
    """
    if not settings.GROQ_API_KEY:
        msg = "GROQ_API_KEY is not configured."
        logger.error(msg)
        return "", msg

    try:
        client = AsyncGroq(
            api_key=settings.GROQ_API_KEY,
            timeout=settings.REQUEST_TIMEOUT,
        )

        completion = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. Provide clear, "
                        "concise, and accurate answers. Use markdown formatting."
                    ),
                },
                {"role": "user", "content": task_description},
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        text = completion.choices[0].message.content or ""
        text = text.strip()

        if not text:
            return "", "Groq returned an empty response."

        logger.info("Groq: received %d characters.", len(text))
        return text, None

    except AuthenticationError:
        msg = "Groq authentication failed. Please check your GROQ_API_KEY."
        logger.error(msg)
        return "", msg
    except APITimeoutError:
        msg = f"Groq request timed out after {settings.REQUEST_TIMEOUT}s."
        logger.error(msg)
        return "", msg
    except APIError as exc:
        msg = f"Groq API error {exc.status_code}: {exc.message}"
        logger.error(msg)
        return "", msg
    except Exception as exc:
        msg = f"Unexpected Groq error: {exc}"
        logger.error(msg)
        return "", msg
