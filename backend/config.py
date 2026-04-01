"""
Application settings loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration for the Autonomous Content Factory."""

    # ── LLM Provider ──
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia")

    # ── NVIDIA NIM ──
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # ── Ollama (local) ──
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    # ── Groq (cloud) ──
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    # ── Editor settings ──
    MAX_EDITOR_RETRIES: int = int(os.getenv("MAX_EDITOR_RETRIES", "1"))


settings = Settings()