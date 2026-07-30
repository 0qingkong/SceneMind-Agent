[CmdletBinding()]
param(
    [switch]$ConfirmReset,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
Import-SceneMindEnv

if (-not $ConfirmReset) {
    $answer = Read-Host "Type RESET to remove only demo-marked rows and demo image files"
    if ($answer -cne "RESET") { throw "Demo reset cancelled; no data was changed." }
}
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }
$arguments = @("-m", "app.cli.reset_demo", "--confirm-reset")
if ($Json) { $arguments += "--json" }
Push-Location (Join-Path $projectRoot "backend")
$savedPythonEncoding = $env:PYTHONIOENCODING
try {
    $env:PYTHONIOENCODING = "utf-8"
    & $pythonExe @arguments
    if ($LASTEXITCODE -ne 0) { throw "Demo reset command failed." }
} finally {
    if ($null -eq $savedPythonEncoding) { Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue } else { $env:PYTHONIOENCODING = $savedPythonEncoding }
    Pop-Location
}
