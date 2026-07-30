[CmdletBinding()]
param([switch]$Force)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")

$stopped = 0
foreach ($role in @("frontend", "backend")) {
    $path = Get-SceneMindPidPath $role
    if (Stop-SceneMindManagedProcess -MetadataPath $path -Force:$Force) {
        Write-Host "Stopped managed SceneMind $role process." -ForegroundColor Green
        $stopped += 1
    } else {
        Write-Host "No verified SceneMind $role process was running; stale metadata was removed." -ForegroundColor Yellow
    }
}
Write-Host "Stop complete. Preserved logs under .runtime\logs ($stopped process roots stopped)."
