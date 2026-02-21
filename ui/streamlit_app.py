"""
STEP 7 — Streamlit chat UI.
Message input, history, API call to backend /chat, display reply.
Modular: uses ui.config (no hardcoded keys), ui.schemas, ui.api_client.
"""
import sys
from pathlib import Path

# Ensure project root on path when run from any cwd
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from ui.api_client import chat
from ui.config import BACKEND_URL


def _ensure_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None


def _render_history():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def main():
    st.set_page_config(page_title="Real Estate Support", page_icon="🏠", layout="centered")
    st.title("Real Estate Support Triage")
    st.caption(f"Backend: {BACKEND_URL}")

    _ensure_session_state()
    _render_history()

    if prompt := st.chat_input("Type your message..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = chat(prompt, st.session_state.get("session_id"))
                    st.markdown(reply)
                    st.session_state["messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Could not reach the server. Error: {e}")
                    st.info("Ensure the backend is running and BACKEND_URL is correct.")


if __name__ == "__main__":
    main()
