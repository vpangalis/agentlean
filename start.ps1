# CoSolve startup script

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.venv\Scripts\activate

# Always sync with origin before starting — prevents running stale local code
Write-Host "Syncing with origin/architecture-refactor..." -ForegroundColor Cyan
$dirty = git status --porcelain
if ($dirty) {
    Write-Host "WARNING: uncommitted local changes detected:" -ForegroundColor Yellow
    Write-Host $dirty -ForegroundColor Yellow
    Write-Host "Fetching and hard-resetting to origin/architecture-refactor..." -ForegroundColor Yellow
    git fetch origin architecture-refactor
    git reset --hard origin/architecture-refactor
} else {
    git pull origin architecture-refactor
}

Write-Host "Starting CoSolve server on port 8010..." -ForegroundColor Cyan
uvicorn backend.app:app --workers 4 --port 8010 --log-level info
