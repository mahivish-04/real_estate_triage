@echo off
cd /d "%~dp0"
if not exist .env copy .env.example .env
echo Starting backend at http://localhost:8000
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
pause
