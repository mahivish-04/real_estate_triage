# Real Estate Triage - Install and run (PowerShell)
# Run this from the real_estate_triage folder in PowerShell.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== 1. Installing dependencies ===" -ForegroundColor Cyan
python -m pip install -r requirements.txt
if (-not $?) { Write-Host "Install failed. Ensure Python is installed and in PATH." -ForegroundColor Red; exit 1 }

if (-not (Test-Path ".env")) {
    Write-Host "`n=== 2. Creating .env from .env.example ===" -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "Edit .env and set LLM_PROVIDER and your API key (e.g. OPENAI_API_KEY), then run this script again." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n=== 3. Ingesting RAG data (if needed) ===" -ForegroundColor Cyan
python -c "import sys; sys.path.insert(0, '.'); from rag.ingest import ensure_knowledge_base; n = ensure_knowledge_base(); print('Knowledge base ready. Chunks:', n)"

Write-Host "`n=== 4. Starting backend on http://localhost:8000 ===" -ForegroundColor Cyan
Write-Host "In another terminal run: streamlit run ui/streamlit_app.py" -ForegroundColor Yellow
Start-Process python -ArgumentList "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow
Start-Sleep -Seconds 3
Write-Host "Backend started. Open http://localhost:8000/health to check." -ForegroundColor Green
Write-Host "To run the UI, open a NEW PowerShell here and run: streamlit run ui/streamlit_app.py" -ForegroundColor Green
