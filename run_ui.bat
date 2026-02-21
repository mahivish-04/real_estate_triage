@echo off
cd /d "%~dp0"
echo Make sure the backend is running (run_backend.bat) first.
echo Starting Streamlit UI...
python -m streamlit run ui/streamlit_app.py
pause
