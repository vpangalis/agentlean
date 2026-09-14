Set-Location $PSScriptRoot
# Agent Improve — start script
# Hard-resets to origin/main then starts the backend
# WARNING: uncommitted changes will be lost
#
# Set-Location is the FIRST line deliberately, because EVERY path below is
# relative and two of them are load-bearing:
#   - `git reset --hard origin/main` resolves against the CURRENT directory,
#     so running this from another repository’s folder would hard-reset THAT
#     repository. That is the dangerous one.
#   - backend/app.py mounts StaticFiles(directory="ui"), so a wrong cwd starts
#     the backend and serves no UI — it looks like it worked.

Write-Host "Resetting to origin/main..." -ForegroundColor Yellow
git fetch origin
git reset --hard origin/main

Write-Host "Activating venv..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

Write-Host "Starting Agent Improve on port 8020..." -ForegroundColor Green
uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload
