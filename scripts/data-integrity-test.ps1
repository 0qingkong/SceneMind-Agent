[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$KeepRuntime
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")

$projectRoot = Get-SceneMindProjectRoot
$runId = "integrity-{0}-{1}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $PID
$resultRoot = Join-Path (Get-SceneMindRuntimeRoot) "test-results\$runId"
$isolatedRoot = Join-Path $resultRoot "isolated"
New-Item -ItemType Directory -Path $isolatedRoot -Force | Out-Null

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }
$database = Join-Path $isolatedRoot "integrity.db"
$storage = Join-Path $isolatedRoot "images"
$backend = Join-Path $projectRoot "backend"

Push-Location $backend
try {
    $output = & $python -m app.cli.check_integrity --database $database --storage $storage --seed-demo --json
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($exitCode -ne 0) { throw "Data-integrity validation failed: $output" }
$summaryPath = Join-Path $resultRoot "summary.json"
$output | Set-Content -LiteralPath $summaryPath -Encoding UTF8

if ($Json) { $output } else {
    ($output | ConvertFrom-Json).checks | ForEach-Object {
        Write-Host ("{0} {1}: {2}" -f $(if ($_.passed) { "PASS" } else { "FAIL" }), $_.name, $_.detail)
    }
    Write-Host "Data-integrity validation passed." -ForegroundColor Green
}
if (-not $KeepRuntime) { Remove-Item -LiteralPath $isolatedRoot -Recurse -Force }
