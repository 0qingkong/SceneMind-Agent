$ErrorActionPreference = "Stop"

Write-Host "== SceneMind Agent setup ==" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python 3.11 or later."
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js was not found. Install Node.js 20.19+ or 22.12+."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Reinstall Node.js with npm."
}

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $projectRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv .venv
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

Write-Host "Installing backend dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r "backend\requirements.txt"

Write-Host "Installing frontend dependencies..."
Push-Location "frontend"
try {
    npm install
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup completed." -ForegroundColor Green
Write-Host "Start backend:  .\scripts\dev-backend.ps1"
Write-Host "Start frontend: .\scripts\dev-frontend.ps1"
