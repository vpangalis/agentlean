@echo off
cd /d "%~dp0\.."
set PYTHONPATH=agent-resolve
call .venv\Scripts\activate
uvicorn backend.app:app --reload --port 8010 --log-level info --reload-exclude "agent-resolve/logs/*"
pause
