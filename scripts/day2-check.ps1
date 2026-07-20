$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found."
}

Write-Host "Running backend tests..." -ForegroundColor Cyan
Set-Location (Join-Path $projectRoot "backend")
& $pythonExe -m pytest tests -q

Write-Host "Running frontend build..." -ForegroundColor Cyan
Set-Location (Join-Path $projectRoot "frontend")
npm run build

Write-Host "Day 2 checks passed." -ForegroundColor Green
