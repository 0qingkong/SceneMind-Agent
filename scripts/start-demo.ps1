[CmdletBinding()]
param(
    [ValidateSet("A", "B", "C")][string]$Profile = "A",
    [string]$AnalyzerMode = "",
    [switch]$SeedDemo,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$started = New-Object System.Collections.Generic.List[string]

if ($AnalyzerMode -and $AnalyzerMode -notin @("yolo", "mock")) { throw "AnalyzerMode must be yolo or mock." }
$resolvedAnalyzer = if ($AnalyzerMode) { $AnalyzerMode } elseif ($Profile -eq "C") { "mock" } else { "yolo" }
$demoMode = $Profile -eq "C"
$shouldSeed = $SeedDemo -or $Profile -eq "C"

try {
    Write-Host "SceneMind competition profile $Profile" -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot "check-system.ps1")
    if ($LASTEXITCODE -ne 0) { throw "System checks failed. Resolve FAIL rows before startup." }
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot ".venv\Scripts\python.exe")) -or -not (Test-Path -LiteralPath (Join-Path $projectRoot "frontend\node_modules"))) {
        throw "Setup is incomplete. Run .\scripts\setup.ps1 first."
    }
    Initialize-SceneMindRuntime | Out-Null

    & (Join-Path $PSScriptRoot "start-backend.ps1") -AnalyzerMode $resolvedAnalyzer -DemoMode:$demoMode -DemoProfile $Profile -NoReload
    $backendPidPath = Get-SceneMindPidPath "backend"
    $started.Add($backendPidPath)

    & (Join-Path $PSScriptRoot "start-frontend.ps1") -NoOpen
    $frontendPidPath = Get-SceneMindPidPath "frontend"
    $started.Add($frontendPidPath)

    $backend = Read-SceneMindProcessMetadata $backendPidPath
    $frontend = Read-SceneMindProcessMetadata $frontendPidPath
    $url = "http://127.0.0.1:5173/"
    if (-not $NoBrowser) { Start-Process $url }
    Write-Host ""
    Write-Host "SceneMind demo is ready." -ForegroundColor Green
    Write-Host "Profile: $Profile | analyzer: $resolvedAnalyzer | demo data: $shouldSeed"
    Write-Host "Frontend: $url | API: http://127.0.0.1:8000/docs"
    Write-Host "PIDs: backend=$($backend.pid), frontend=$($frontend.pid)"
    Write-Host "Logs: .runtime\logs"
    Write-Host "Stop: .\scripts\stop-demo.ps1"
} catch {
    for ($index = $started.Count - 1; $index -ge 0; $index--) {
        Stop-SceneMindManagedProcess -MetadataPath $started[$index] -Force | Out-Null
    }
    throw
}
