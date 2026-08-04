[CmdletBinding()]
param(
    [Alias("Host")][string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [ValidateSet("yolo", "mock")][string]$AnalyzerMode = "yolo",
    [bool]$DemoMode = $false,
    [ValidateSet("A", "B", "C", "none")][string]$DemoProfile = "none",
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
Import-SceneMindEnv
Initialize-SceneMindRuntime | Out-Null

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }
$pidPath = Get-SceneMindPidPath "backend"
$existing = Read-SceneMindProcessMetadata $pidPath
if ($existing -and (Test-SceneMindProcessIdentity $existing)) { throw "SceneMind backend is already running with PID $($existing.pid)." }
if (Test-Path -LiteralPath $pidPath) { Remove-Item -LiteralPath $pidPath -Force }
if (-not (Test-SceneMindPortAvailable -Port $Port -HostAddress $BindHost)) { throw "Backend port $Port is occupied. See docs/RECOVERY.md." }

$logRoot = Join-Path (Get-SceneMindRuntimeRoot) "logs"
$stdoutLog = Join-Path $logRoot "backend.out.log"
$stderrLog = Join-Path $logRoot "backend.err.log"
$backendRoot = Join-Path $projectRoot "backend"
$savedAnalyzer = $env:ANALYZER_MODE
$savedDemo = $env:DEMO_MODE
$savedProfile = $env:DEMO_PROFILE
$savedBuild = $env:APP_BUILD
try {
    # Managed competition startup must report the build shipped by this
    # repository even when an older local .env survives an upgrade.
    $env:APP_BUILD = "day19-20-release-candidate"
    $env:ANALYZER_MODE = $AnalyzerMode
    $env:DEMO_MODE = $DemoMode.ToString().ToLowerInvariant()
    $env:DEMO_PROFILE = $DemoProfile
    $arguments = @("-m", "uvicorn", "app.main:app", "--host", $BindHost, "--port", [string]$Port)
    $process = Start-Process -FilePath $pythonExe -ArgumentList $arguments -WorkingDirectory $backendRoot -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru -WindowStyle Hidden
} finally {
    if ($null -eq $savedAnalyzer) { Remove-Item Env:ANALYZER_MODE -ErrorAction SilentlyContinue } else { $env:ANALYZER_MODE = $savedAnalyzer }
    if ($null -eq $savedDemo) { Remove-Item Env:DEMO_MODE -ErrorAction SilentlyContinue } else { $env:DEMO_MODE = $savedDemo }
    if ($null -eq $savedProfile) { Remove-Item Env:DEMO_PROFILE -ErrorAction SilentlyContinue } else { $env:DEMO_PROFILE = $savedProfile }
    if ($null -eq $savedBuild) { Remove-Item Env:APP_BUILD -ErrorAction SilentlyContinue } else { $env:APP_BUILD = $savedBuild }
}
Save-SceneMindProcessMetadata -Process $process -Role "backend" -Command "uvicorn app.main:app" -Extra @{ port = $Port; analyzer_mode = $AnalyzerMode; demo_mode = $DemoMode; profile = $DemoProfile; stdout_log = $stdoutLog; stderr_log = $stderrLog } | Out-Null

$readyUri = "http://127.0.0.1:$Port/api/v1/ready"
$ready = Wait-SceneMindHttp -Uri $readyUri -TimeoutSeconds 60 -Validator { param($response) $response.status -eq "ready" }
if (-not $ready) {
    Stop-SceneMindManagedProcess -MetadataPath $pidPath -Force | Out-Null
    $tail = Get-SceneMindLogTail $stderrLog
    throw "Backend did not become ready at $readyUri.`n$tail"
}
Write-Host "Backend ready: http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "PID $($process.Id) | logs: $stdoutLog / $stderrLog"
