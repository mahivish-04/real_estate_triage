"""
Return the configured LangChain chat model (OpenAI / Gemini / Groq / Ollama).
Uses env: LLM_PROVIDER, OPENAI_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY, OLLAMA_*.
"""
import os
import sys
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GEMINI_MODEL,
)


def get_llm():
    """Return ChatModel for classification. Prefer OpenAI/Gemini/Groq; fallback Ollama."""
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0,
        )
    if LLM_PROVIDER == "gemini" and GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0,
        )
    if LLM_PROVIDER == "groq" and GROQ_API_KEY:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0,
        )
    # Fallback: Ollama (local)
    from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOllama
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0,
    )
