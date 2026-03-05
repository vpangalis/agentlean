# CoSolve startup script
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.venv\Scripts\activate

Write-Host "Starting CoSolve server on port 8010..." -ForegroundColor Cyan
uvicorn backend.app:app --workers 4 --port 8010 --log-level info
