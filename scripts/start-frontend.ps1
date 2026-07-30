[CmdletBinding()]
param(
    [Alias("Host")][string]$BindHost = "127.0.0.1",
    [int]$Port = 5173,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
Initialize-SceneMindRuntime | Out-Null

$frontendRoot = Join-Path $projectRoot "frontend"
if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot "node_modules"))) { throw "Missing frontend/node_modules. Run .\scripts\setup.ps1 first." }
$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { $npm = Get-Command npm -ErrorAction SilentlyContinue }
if (-not $npm) { throw "npm is unavailable." }
$pidPath = Get-SceneMindPidPath "frontend"
$existing = Read-SceneMindProcessMetadata $pidPath
if ($existing -and (Test-SceneMindProcessIdentity $existing)) { throw "SceneMind frontend is already running with PID $($existing.pid)." }
if (Test-Path -LiteralPath $pidPath) { Remove-Item -LiteralPath $pidPath -Force }
if (-not (Test-SceneMindPortAvailable -Port $Port -HostAddress $BindHost)) { throw "Frontend port $Port is occupied. See docs/RECOVERY.md." }
if ($BindHost -ne "127.0.0.1" -and $BindHost -ne "localhost") { Write-Warning "LAN mode was explicitly requested. Physical-phone camera access generally requires trusted HTTPS." }

$logRoot = Join-Path (Get-SceneMindRuntimeRoot) "logs"
$stdoutLog = Join-Path $logRoot "frontend.out.log"
$stderrLog = Join-Path $logRoot "frontend.err.log"
$arguments = @("run", "dev", "--", "--host", $BindHost, "--port", [string]$Port, "--strictPort")
$process = Start-Process -FilePath $npm.Source -ArgumentList $arguments -WorkingDirectory $frontendRoot -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru -WindowStyle Hidden
Save-SceneMindProcessMetadata -Process $process -Role "frontend" -Command "npm run dev" -Extra @{ port = $Port; host_address = $BindHost; stdout_log = $stdoutLog; stderr_log = $stderrLog } | Out-Null

$url = "http://127.0.0.1:$Port/"
if (-not (Wait-SceneMindHttp -Uri $url -TimeoutSeconds 45)) {
    Stop-SceneMindManagedProcess -MetadataPath $pidPath -Force | Out-Null
    $tail = Get-SceneMindLogTail $stderrLog
    throw "Frontend did not respond at $url.`n$tail"
}
Write-Host "Frontend ready: $url" -ForegroundColor Green
Write-Host "PID $($process.Id) | logs: $stdoutLog / $stderrLog"
if (-not $NoOpen) { Start-Process $url }
