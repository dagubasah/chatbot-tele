# config/llm_config.py

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def validate_llm_config() -> None:
    """
    Pastikan API key ada sebelum client dipakai.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY belum di-set di file .env")