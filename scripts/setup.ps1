[CmdletBinding()]
param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$Force,
    [switch]$DownloadModel
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")

$projectRoot = Get-SceneMindProjectRoot
Write-Host "== SceneMind Agent setup ==" -ForegroundColor Cyan
Initialize-SceneMindRuntime | Out-Null

$envFile = Join-Path $projectRoot ".env"
$exampleEnv = Join-Path $projectRoot ".env.example"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath $exampleEnv -Destination $envFile
    Write-Host "Created .env from .env.example (existing files are never overwritten)."
} else {
    Write-Host "Keeping existing .env."
}

if (-not $SkipBackend) {
    $pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $pythonExe)) {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $pythonCommand) { throw "Python was not found. Install Python 3.11 or later." }
        Write-Host "Creating Python virtual environment..."
        & $pythonCommand.Source -m venv (Join-Path $projectRoot ".venv")
    }
    if ($Force -or -not (Test-Path -LiteralPath (Join-Path $projectRoot ".venv\pyvenv.cfg"))) {
        Write-Host "Refreshing Python virtual environment metadata..."
    }
    Write-Host "Installing backend dependencies..."
    & $pythonExe -m pip install -r (Join-Path $projectRoot "backend\requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }

    if ($DownloadModel) {
        Import-SceneMindEnv
        $modelName = if ($env:YOLO_MODEL) { $env:YOLO_MODEL } else { "yolo26n.pt" }
        Write-Host "Explicitly downloading/configuring YOLO model: $modelName"
        & $pythonExe -c "import os; from ultralytics import YOLO; YOLO(os.environ.get('YOLO_MODEL', 'yolo26n.pt')); print('Model is available.')"
        if ($LASTEXITCODE -ne 0) { throw "Explicit model download failed." }
    } else {
        Write-Host "YOLO weights were not downloaded. Use -DownloadModel to request that explicitly."
    }
}

if (-not $SkipFrontend) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js was not found. Install Node.js 20.19+ or 22.12+." }
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($null -eq $npm) { $npm = Get-Command npm -ErrorAction SilentlyContinue }
    if ($null -eq $npm) { throw "npm was not found. Reinstall Node.js with npm." }
    $frontendRoot = Join-Path $projectRoot "frontend"
    $npmCache = Join-Path (Get-SceneMindRuntimeRoot) "npm-cache"
    Push-Location $frontendRoot
    try {
        if (Test-Path -LiteralPath (Join-Path $frontendRoot "package-lock.json")) {
            Write-Host "Installing frontend dependencies with npm ci..."
            & $npm.Source ci --cache $npmCache $(if ($Force) { "--force" } else { "--prefer-offline" })
        } else {
            Write-Host "Installing frontend dependencies with npm install..."
            & $npm.Source install --cache $npmCache
        }
        if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    } finally {
        Pop-Location
    }
}

Write-Host "Setup completed." -ForegroundColor Green
Write-Host "Start all: .\scripts\start-demo.ps1 -Profile A"
