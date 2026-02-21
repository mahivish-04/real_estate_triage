@echo off
cd /d "%~dp0"
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed. Make sure Python is installed and in PATH.
    pause
    exit /b 1
)
if not exist .env (
    copy .env.example .env
    echo Created .env. Please edit it and set LLM_PROVIDER and your API key.
)
echo Done. Use run_backend.bat then run_ui.bat to start.
pause
