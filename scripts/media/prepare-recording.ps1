[CmdletBinding()]
param(
    [ValidateSet("B", "C")][string]$Profile = "C",
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "..\lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$runId = "recording-{0}-{1}" -f $Profile.ToLowerInvariant(), (Get-Date -Format "yyyyMMdd-HHmmss")
$sessionRoot = Join-Path $projectRoot (Join-Path ".runtime\recording" $runId)
New-Item -ItemType Directory -Path $sessionRoot -Force | Out-Null
$statusPath = Join-Path $sessionRoot "status.json"
$steps = New-Object System.Collections.Generic.List[object]
$powershell = (Get-Command powershell.exe -ErrorAction Stop).Source

function Add-Step([string]$Name, [string]$Status, [string]$Detail) {
    $steps.Add([pscustomobject]@{ name = $Name; status = $Status; detail = $Detail })
}
function Save-Status([string]$Status, [string]$ErrorMessage = "") {
    [ordered]@{
        run_id = $runId
        profile = $Profile
        status = $Status
        recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        start_url = "http://127.0.0.1:5173/"
        api_url = "http://127.0.0.1:8000/api/v1"
        steps = @($steps | ForEach-Object { $_ })
        error = $ErrorMessage
        human_gates = @("screen recording NOT RUN", "voice-over approval NOT RUN", "privacy review NOT RUN")
    } | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $statusPath -Encoding UTF8
}
function Invoke-CheckedScript([string]$Path, [string[]]$Arguments = @()) {
    & $powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Script failed with exit code $LASTEXITCODE`: $Path" }
}

try {
    foreach ($relative in @("docs\DEMO_RUNBOOK.md", "docs\TEST_REPORT.md", "docs\EVALUATION.md", "docs\demo\LIVE_DEMO_CUE_SHEET.md")) {
        if (-not (Test-Path -LiteralPath (Join-Path $projectRoot $relative))) { throw "Readiness document missing: $relative" }
    }
    Add-Step "Day 13/14/15 evidence" "PASS" "Runbook, test report, evaluation and cue sheet are present."

    Invoke-CheckedScript -Path (Join-Path $PSScriptRoot "verify-demo-assets.ps1") -Arguments @("-Profile", $Profile)
    Add-Step "Demo assets" "PASS" "Profile $Profile asset policy passed."

    Invoke-CheckedScript -Path (Join-Path $projectRoot "scripts\stop-demo.ps1") -Arguments @("-Force")
    Add-Step "Managed process cleanup" "PASS" "Stopped only SceneMind processes verified by PID metadata."

    Invoke-CheckedScript -Path (Join-Path $projectRoot "scripts\check-system.ps1")
    Add-Step "System readiness" "PASS" "Runtime, dependencies and ports passed."

    if ($Profile -eq "C") {
        Invoke-CheckedScript -Path (Join-Path $projectRoot "scripts\reset-demo.ps1") -Arguments @("-ConfirmReset", "-Json")
        Add-Step "Demo reset" "PASS" "Only demo-marked rows/files were reset."
    }

    Invoke-CheckedScript -Path (Join-Path $projectRoot "scripts\start-demo.ps1") -Arguments @("-Profile", $Profile, "-NoBrowser")
    Add-Step "Startup" "PASS" "Backend and frontend started with managed PID/log metadata."

    Invoke-CheckedScript -Path (Join-Path $projectRoot "scripts\smoke-demo.ps1") -Arguments @("-Extended")
    Add-Step "API smoke" "PASS" "Liveness, readiness, Memory, Agent, sessions, devices and insights passed."

    $routes = @("/", "/live", "/analyze", "/memory", "/agent", "/sessions", "/devices", "/glasses", "/insights", "/privacy", "/system")
    foreach ($route in $routes) {
        $response = Invoke-WebRequest -Uri ("http://127.0.0.1:5173" + $route) -UseBasicParsing -TimeoutSec 10
        if ([int]$response.StatusCode -ne 200) { throw "Route $route returned HTTP $($response.StatusCode)." }
    }
    Add-Step "Frontend routes" "PASS" "$($routes.Count) recording routes returned HTTP 200."

    Save-Status "ready"
    Write-Host ""
    Write-Host "Recording preflight READY: $runId" -ForegroundColor Green
    Write-Host "Status: $statusPath"
    Write-Host "Cue sheet (maximum 5 minutes):" -ForegroundColor Cyan
    Get-Content -LiteralPath (Join-Path $projectRoot "docs\demo\LIVE_DEMO_CUE_SHEET.md") -Encoding UTF8 | Select-String "^\| [0-9]" | ForEach-Object { Write-Host $_.Line }
    if (-not $NoBrowser) { Start-Process "http://127.0.0.1:5173/" }
} catch {
    Add-Step "Preflight" "FAIL" $_.Exception.Message
    Save-Status "failed" $_.Exception.Message
    & $powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot "scripts\stop-demo.ps1") -Force 2>$null
    Write-Host "Recording preflight FAILED. Status: $statusPath" -ForegroundColor Red
    throw
}
