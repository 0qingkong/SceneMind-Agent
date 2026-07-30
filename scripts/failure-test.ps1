[CmdletBinding()]
param(
    [ValidateSet("all", "api", "process")][string]$Category = "all",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$runId = "failure-{0}-{1}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $PID
$resultRoot = Join-Path (Get-SceneMindRuntimeRoot) "test-results\$runId"
New-Item -ItemType Directory -Path $resultRoot -Force | Out-Null
$results = New-Object System.Collections.Generic.List[object]

function Add-Result([string]$Name, [bool]$Passed, [string]$Detail) {
    $results.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail })
    if (-not $Json) { Write-Host ("{0} {1}: {2}" -f $(if ($Passed) { "PASS" } else { "FAIL" }), $Name, $Detail) }
}

if ($Category -in @("all", "api")) {
    Push-Location (Join-Path $projectRoot "backend")
    try {
        & (Join-Path $projectRoot ".venv\Scripts\python.exe") -m pytest tests/e2e/test_failure_injection.py -q --basetemp (Join-Path $resultRoot "pytest") -p no:cacheprovider
        Add-Result "api_failure_injection" ($LASTEXITCODE -eq 0) "controlled API failures"
    } finally { Pop-Location }
}

if ($Category -in @("all", "process")) {
    $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0)
    $listener.Start()
    try {
        $port = ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
        Add-Result "occupied_port" (-not (Test-SceneMindPortAvailable -Port $port)) "owned listener was not taken over"
    } finally { $listener.Stop() }

    $stalePath = Get-SceneMindPidPath "day14-stale"
    @{ role = "day14-stale"; pid = 999999; process_name = "missing"; start_time_utc = "2000-01-01T00:00:00Z" } |
        ConvertTo-Json | Set-Content -LiteralPath $stalePath -Encoding UTF8
    $stopped = Stop-SceneMindManagedProcess -MetadataPath $stalePath
    Add-Result "stale_pid" ((-not $stopped) -and -not (Test-Path $stalePath)) "stale metadata removed without process termination"

    $child = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-Command", "Start-Sleep -Seconds 30") -PassThru -WindowStyle Hidden
    $managedPath = Get-SceneMindPidPath "day14-owned"
    Save-SceneMindProcessMetadata -Process $child -Role "day14-owned" -Command "controlled test sleeper" | Out-Null
    $managedStopped = Stop-SceneMindManagedProcess -MetadataPath $managedPath -Force
    Start-Sleep -Milliseconds 250
    Add-Result "owned_process_stop" ($managedStopped -and -not (Get-Process -Id $child.Id -ErrorAction SilentlyContinue) -and -not (Test-Path $managedPath)) "verified owned process and metadata cleaned"
}

$summary = [pscustomobject]@{ run_id = $runId; category = $Category; ok = -not ($results | Where-Object { -not $_.passed }); results = $results }
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $resultRoot "summary.json") -Encoding UTF8
if ($Json) { $summary | ConvertTo-Json -Depth 5 }
if (-not $summary.ok) { exit 1 }
