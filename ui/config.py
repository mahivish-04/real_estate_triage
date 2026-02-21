"""
UI configuration from environment. No hardcoded API keys or URLs.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Backend API base URL (used by Streamlit to call /chat)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# Timeout for chat API call (seconds)
CHAT_TIMEOUT = int(os.getenv("CHAT_TIMEOUT", "60"))
