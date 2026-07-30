[CmdletBinding()]
param(
    [switch]$ResetFirst,
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
Import-SceneMindEnv
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }

$arguments = @("-m", "app.cli.seed_demo")
if ($ResetFirst) { $arguments += "--reset-first" }
if ($Json) { $arguments += "--json" }
Push-Location (Join-Path $projectRoot "backend")
$savedPythonEncoding = $env:PYTHONIOENCODING
try {
    $env:PYTHONIOENCODING = "utf-8"
    & $pythonExe @arguments
    if ($LASTEXITCODE -ne 0) { throw "Demo seed command failed." }
} finally {
    if ($null -eq $savedPythonEncoding) { Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue } else { $env:PYTHONIOENCODING = $savedPythonEncoding }
    Pop-Location
}
