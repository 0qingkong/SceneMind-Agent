$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found. Run .\scripts\setup.ps1 first."
}

Set-Location (Join-Path $projectRoot "backend")
& $pythonExe -m fastapi dev app\main.py
