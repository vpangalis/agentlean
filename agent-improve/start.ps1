# Agent Improve — start script
# Hard-resets to origin/main then starts the backend
# WARNING: uncommitted changes will be lost

Write-Host "Resetting to origin/main..." -ForegroundColor Yellow
git fetch origin
git reset --hard origin/main

Write-Host "Activating venv..." -ForegroundColor Yellow
..venvScriptsActivate.ps1

Write-Host "Starting Agent Improve on port 8020..." -ForegroundColor Green
uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload
