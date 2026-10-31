<#
.SYNOPSIS
  The founder's walk server at one commit (founder ruling 2026-10-30): a locked worktree in Temp, the root .env copied,
  uvicorn started detached so it outlives the session that started it, and ready on /health.
.DESCRIPTION
  Refuses when the port is already in use: the walk server is the founder's while they walk, and is never restarted
  without telling them first. Stop the running one by hand, then run this.
.EXAMPLE
  & agent-improve/scripts/walk_server.ps1 ff508e7
#>
param(
    [Parameter(Mandatory = $true)][string]$Commit,
    [int]$Port = 8020,
    [int]$WaitSeconds = 120
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

# A server that answers is a server that runs: the listener table is not visible from every shell (a sandboxed one
# sees none), so the health endpoint is asked too.
$busy = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
$answering = $false
try { $answering = [bool](Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 3) } catch { }
if ($busy -or $answering) {
    throw "port $Port is in use: the walk server runs; never restart it during a walk without telling the founder"
}

$sha = (git -C $repo rev-parse --short=7 "$Commit^{commit}")
if ($LASTEXITCODE -ne 0 -or -not $sha) { throw "no commit '$Commit' in $repo" }
$sha = $sha.Trim()
$wt = Join-Path $env:TEMP "agentlean-walk-$sha"
if (-not (Test-Path $wt)) {
    git -C $repo worktree add --quiet --detach $wt $sha
    if ($LASTEXITCODE -ne 0) { throw "git worktree add failed for $sha" }
    git -C $repo worktree lock --reason "founder walk server :$Port" $wt
    if ($LASTEXITCODE -ne 0) { throw "git worktree lock failed for $wt" }
}
Copy-Item -LiteralPath (Join-Path $repo '.env') -Destination (Join-Path $wt '.env') -Force   # the one root .env

$py = Join-Path $repo 'agent-improve\.venv\Scripts\python.exe'
$p = Start-Process -FilePath $py -ArgumentList '-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', "$Port" `
    -WorkingDirectory (Join-Path $wt 'agent-improve') -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $wt "server-$Port.out.log") -RedirectStandardError (Join-Path $wt "server-$Port.log") -PassThru

$deadline = (Get-Date).AddSeconds($WaitSeconds)
$ok = $false
do {
    Start-Sleep -Seconds 3
    try { $ok = (Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 5).StatusCode -eq 200 } catch { $ok = $false }
} until ($ok -or $p.HasExited -or (Get-Date) -gt $deadline)
Start-Sleep -Seconds 2
if (-not $ok -or $p.HasExited) {
    Get-Content -LiteralPath (Join-Path $wt "server-$Port.log") -Tail 15
    throw "the walk server did not come up on :$Port (see $wt\server-$Port.log)"
}
"UP $(Get-Date -Format HH:mm:ss) on $sha, port $Port, pid $($p.Id), worktree $wt"
