$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location (Join-Path $projectRoot "frontend")

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev
