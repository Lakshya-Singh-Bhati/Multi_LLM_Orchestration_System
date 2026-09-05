"""
config.py
---------
Centralised configuration loader.
Reads environment variables from the .env file using python-dotenv.
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


class Settings:
    """Application-level settings derived from environment variables."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Gemini model to use
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Groq model to use
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    # Request timeout (seconds)
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    def validate(self) -> list[str]:
        """
        Return a list of validation errors.
        An empty list means configuration is valid.
        """
        errors: list[str] = []
        if not self.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set in the .env file.")
        if not self.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set in the .env file.")
        return errors


# Singleton instance used across the application
settings = Settings()
