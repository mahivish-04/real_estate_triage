# Real Estate Support Triage Agent

AI-powered chatbot: classify intent, extract entities, RAG over knowledge base, run tools, return professional reply.

---

## How to install

**Option A — Quick (Windows):**  
Double-click `install.bat` in the project folder. Then edit `.env` to set `LLM_PROVIDER` and your API key. To run: double-click `run_backend.bat`, then in a second window double-click `run_ui.bat`.

**Option B — Manual:**

1. **Go to project root:** `cd real_estate_triage`

2. **Create a virtual environment** (recommended):  
   `python -m venv venv` then `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)

3. **Install dependencies:**  
   `pip install -r requirements.txt`

4. **Configure environment** (no hardcoded API keys):  
   `copy .env.example .env` (Windows) or `cp .env.example .env` (Linux/macOS)  
   Edit `.env`: set `LLM_PROVIDER` and the matching API key (e.g. `OPENAI_API_KEY`). Optional: `BACKEND_URL` for the UI (default `http://localhost:8000`).

---

## How to run the backend

From the **project root** `real_estate_triage/`:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

- Health check: **GET** `http://localhost:8000/health`
- Chat: **POST** `http://localhost:8000/chat` with body `{"message": "your text", "session_id": "optional"}` → response `{"reply": "..."}`

---

## How to ingest data

The backend **auto-ingests** on startup: at first run it loads all `.txt` files from `data/`, chunks them, builds embeddings, and stores them in ChromaDB (under `chroma_db/` by default).

To **re-ingest** (e.g. after adding or editing files in `data/`):

1. **Option A — restart the backend**  
   Delete the ChromaDB directory so the next startup sees an empty collection and runs ingest again:

   ```bash
   # From project root
   rmdir /s /q chroma_db   # Windows
   # rm -rf chroma_db     # Linux/macOS
   ```

   Then start the backend as above.

2. **Option B — run ingest from Python** (from project root):

   ```bash
   python -c "
   import sys; sys.path.insert(0, '.')
   from rag.ingest import run_ingest
   n = run_ingest()
   print(f'Ingested {n} chunks.')
   "
   ```

   Then restart the backend if it was already running (so it uses the updated index).

Data files: add or edit `.txt` files in `data/` (e.g. `sample_properties.txt`, `payment_policy.txt`). Content is chunked (500 chars, 50 overlap), embedded with sentence-transformers, and stored in ChromaDB.

---

## How to run the UI

1. **Start the backend** first (see [How to run the backend](#how-to-run-the-backend)).

2. From the **project root** `real_estate_triage/`:

   ```bash
   streamlit run ui/streamlit_app.py
   ```

   Or:

   ```bash
   python -m streamlit run ui/streamlit_app.py
   ```

3. Open the URL shown in the terminal (usually `http://localhost:8501`). Use the chat input to send messages; replies come from the backend `/chat` API. History is shown in the same page.

If the UI cannot reach the backend, set `BACKEND_URL` in `.env` (e.g. `http://127.0.0.1:8000`) and restart Streamlit.

---

## Steps implemented

- **Step 1** — FastAPI server with `POST /chat`: request `{ "message", "session_id"? }`, response `{ "reply" }`.
- **Step 2** — LLM classifier + NER (structured JSON): `intent`, `urgency`, `entities`.
- **Step 3** — RAG: load `data/*.txt`, chunk, embed, ChromaDB; retriever top 5.
- **Step 4** — Deterministic tools (no LLM): `schedule_visit`, `fetch_documents`, `generate_receipt`, `knowledge_search`; ask for clarification when entities missing.
- **Step 5** — Orchestrator: classify → retrieve → choose tool → execute → generate response.
- **Step 6** — LLM response: professional reply from message + triage + context + tool output; never hallucinate missing data.
- **Step 7** — Streamlit UI: message input, history, API call, display reply; modular, Pydantic schemas, no hardcoded keys.

## Pipeline (orchestrator)

1. **Classify** message (intent, urgency, entities).
2. **Retrieve** RAG context (top 5 chunks).
3. **Choose tool** by intent: `schedule_visit` → schedule_visit, `payment` → generate_receipt, `documents` → fetch_documents, `inquiry` / `complaint` → knowledge_search.
4. **Execute** tool (deterministic; no LLM).
5. **Generate** final reply via LLM (responder) using message + triage + context + tool output.

## Test cases (examples to try in UI or via API)

- `"book visit tomorrow 4pm A-203"` → schedule_visit (date, time, flat extracted).
- `"send brochure for tower B"` → documents/inquiry + knowledge_search (brochure/pricing in RAG).
- `"I paid but no receipt"` → payment → generate_receipt (may ask for flat ID if not in message).
- `"price of 2bhk"` → inquiry → knowledge_search (2BHK pricing in RAG).
- `"water leakage urgent"` → complaint (high urgency) → knowledge_search (maintenance/helpline in RAG).

## Rules (codebase)

- **Modular code**: UI has separate `config`, `schemas`, `api_client`; backend has `orchestrator`, `agent`, `rag`.
- **Pydantic schemas**: Used for API request/response (backend and `ui/schemas.py`).
- **No hardcoded API keys**: All keys and URLs from `.env` (see `.env.example`).
- **Independently testable**: Each module can be imported and tested (e.g. `agent.tools`, `ui.api_client`).
- **Never hallucinate missing data**: Tools return clarification text when required entities are missing; responder prompt instructs the LLM to ask for missing info instead of inventing it.

## Project structure

```
real_estate_triage/
├── backend/     (app.py, orchestrator.py, config.py, schemas.py)
├── agent/       (classifier.py, responder.py, tools.py, prompts.py, llm_factory.py)
├── rag/         (embeddings.py, ingest.py, retriever.py)
├── data/        (*.txt for RAG)
├── ui/          (streamlit_app.py, config.py, schemas.py, api_client.py)
├── .env.example
├── requirements.txt
└── README.md
```
