[CmdletBinding()]
param(
    [switch]$SkipBrowser,
    [switch]$KeepRuntime,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$runId = "e2e-{0}-{1}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $PID
$resultRoot = Join-Path (Get-SceneMindRuntimeRoot) "test-results\$runId"
$isolatedRoot = Join-Path $resultRoot "isolated"
New-Item -ItemType Directory -Path $isolatedRoot -Force | Out-Null
$backendProcess = $null
$frontendProcess = $null
$checks = New-Object System.Collections.Generic.List[object]

function Add-E2eResult([string]$Name, [bool]$Passed, [string]$Detail) {
    $checks.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail })
    if (-not $Json) { Write-Host ("{0} {1}: {2}" -f $(if ($Passed) { "PASS" } else { "FAIL" }), $Name, $Detail) }
    if (-not $Passed) { throw "$Name failed: $Detail" }
}

function Stop-OwnedProcess($Process) {
    if ($null -eq $Process) { return }
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = "SilentlyContinue"
        & taskkill.exe /PID $Process.Id /T /F 2>$null | Out-Null
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    } finally { $ErrorActionPreference = $saved }
}

try {
    $python = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }
    if (-not (Test-Path (Join-Path $projectRoot "frontend\node_modules"))) { throw "Missing frontend/node_modules." }

    Push-Location (Join-Path $projectRoot "backend")
    try {
        & $python -m pytest tests -q --basetemp (Join-Path $resultRoot "pytest") -p no:cacheprovider
        Add-E2eResult "backend_tests" ($LASTEXITCODE -eq 0) "pytest suite"
    } finally { Pop-Location }

    & (Join-Path $PSScriptRoot "data-integrity-test.ps1") -Json | Set-Content -LiteralPath (Join-Path $resultRoot "integrity.json") -Encoding UTF8
    Add-E2eResult "data_integrity" ($LASTEXITCODE -eq 0) "isolated database validation"

    if (-not $SkipBrowser) {
        $backendPort = 18000
        $frontendPort = 15173
        if (-not (Test-SceneMindPortAvailable $backendPort) -or -not (Test-SceneMindPortAvailable $frontendPort)) { throw "Day 14 test ports are occupied." }
        $databasePath = (Join-Path $isolatedRoot "browser.db").Replace("\", "/")
        $storagePath = Join-Path $isolatedRoot "images"
        $env:DATABASE_URL = "sqlite:///$databasePath"
        $env:SCENE_STORAGE_DIR = $storagePath
        $env:ANALYZER_MODE = "mock"
        $env:DEMO_MODE = "true"
        $env:DEMO_PROFILE = "C"
        $env:ALLOWED_ORIGINS = "http://127.0.0.1:$frontendPort"
        $env:VITE_API_BASE_URL = "http://127.0.0.1:$backendPort/api/v1"
        $backendProcess = Start-Process -FilePath $python -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$backendPort") -WorkingDirectory (Join-Path $projectRoot "backend") -RedirectStandardOutput (Join-Path $resultRoot "backend.log") -RedirectStandardError (Join-Path $resultRoot "backend-error.log") -PassThru -WindowStyle Hidden
        if (-not (Wait-SceneMindHttp -Uri "http://127.0.0.1:$backendPort/api/v1/ready" -TimeoutSeconds 45 -Validator { param($response) $response.status -eq "ready" })) { throw "Isolated backend did not become ready." }

        $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
        $frontendProcess = Start-Process -FilePath $npm -ArgumentList @("run", "dev", "--", "--host", "127.0.0.1", "--port", "$frontendPort", "--strictPort") -WorkingDirectory (Join-Path $projectRoot "frontend") -RedirectStandardOutput (Join-Path $resultRoot "frontend.log") -RedirectStandardError (Join-Path $resultRoot "frontend-error.log") -PassThru -WindowStyle Hidden
        if (-not (Wait-SceneMindHttp -Uri "http://127.0.0.1:$frontendPort" -TimeoutSeconds 45)) { throw "Isolated frontend did not become ready." }

        $imagePath = Join-Path $isolatedRoot "permitted-synthetic.png"
        & $python -c "from PIL import Image; Image.new('RGB', (640, 480), 'white').save(r'''$imagePath''')"
        if ($LASTEXITCODE -ne 0) { throw "Unable to create the permitted synthetic browser fixture." }
        $env:SCENEMIND_E2E_BASE_URL = "http://127.0.0.1:$frontendPort"
        $env:SCENEMIND_E2E_API_URL = "http://127.0.0.1:$backendPort/api/v1"
        $env:SCENEMIND_E2E_IMAGE = $imagePath
        $env:SCENEMIND_E2E_REPORT = Join-Path $resultRoot "playwright.json"
        $env:SCENEMIND_E2E_OUTPUT = Join-Path $resultRoot "browser"
        Push-Location (Join-Path $projectRoot "frontend")
        try {
            & $npm run test:e2e
            Add-E2eResult "browser_e2e" ($LASTEXITCODE -eq 0) "six core flows plus four responsive UI reviews"
        } finally { Pop-Location }
    }
} finally {
    Stop-OwnedProcess $frontendProcess
    Stop-OwnedProcess $backendProcess
    @("DATABASE_URL", "SCENE_STORAGE_DIR", "ANALYZER_MODE", "DEMO_MODE", "DEMO_PROFILE", "ALLOWED_ORIGINS", "VITE_API_BASE_URL", "SCENEMIND_E2E_BASE_URL", "SCENEMIND_E2E_API_URL", "SCENEMIND_E2E_IMAGE", "SCENEMIND_E2E_REPORT", "SCENEMIND_E2E_OUTPUT") | ForEach-Object { Remove-Item "Env:$_" -ErrorAction SilentlyContinue }
}

$summary = [pscustomobject]@{ run_id = $runId; ok = -not ($checks | Where-Object { -not $_.passed }); checks = $checks }
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $resultRoot "summary.json") -Encoding UTF8
if ($Json) { $summary | ConvertTo-Json -Depth 5 }
if (-not $KeepRuntime) { Remove-Item -LiteralPath $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue }
if (-not $summary.ok) { exit 1 }
