[CmdletBinding()]
param(
    [string]$Version = "0.9.0-rc1",
    [string]$PackagePath = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$runId = "offline-{0}-{1}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $PID
$runRoot = Join-Path $projectRoot (Join-Path ".runtime\release" $runId)
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
$checks = New-Object System.Collections.Generic.List[object]
$started = $false
$status = "FAIL"
$errorMessage = ""
$savedPipNoIndex = $env:PIP_NO_INDEX
$savedNpmOffline = $env:npm_config_offline

function Add-Check([string]$Name, [bool]$Passed, [string]$Detail) { $checks.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail }) }
try {
    $env:PIP_NO_INDEX = "1"
    $env:npm_config_offline = "true"
    Add-Check "network_policy" $true "Process-local no-index/offline flags set; adapters, firewall and network configuration were not modified."

    $python = Join-Path $projectRoot ".venv\Scripts\python.exe"
    $nodeModules = Join-Path $projectRoot "frontend\node_modules"
    $dependenciesReady = (Test-Path -LiteralPath $python) -and (Test-Path -LiteralPath $nodeModules -PathType Container)
    Add-Check "installed_dependencies" $dependenciesReady "Existing Python and frontend dependencies are required; no install is attempted."
    if (-not $dependenciesReady) { throw "Local dependencies are incomplete; offline check will not make network calls." }

    if (-not $PackagePath) {
        $candidate = Join-Path $projectRoot ".runtime\release\SceneMind-v$Version"
        if (Test-Path -LiteralPath $candidate -PathType Container) { $PackagePath = $candidate }
    }
    if ($PackagePath) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "verify-release.ps1") -Version $Version -PackagePath $PackagePath -Json *> (Join-Path $runRoot "package-verification.log")
        $packageOk = $LASTEXITCODE -eq 0
        Add-Check "package_verification" $packageOk "Release directory was checksum/static verified in a clean temporary inspection directory."
        if (-not $packageOk) { throw "Package verification failed." }
    } else { Add-Check "package_verification" $true "No package path supplied; runtime-only Profile C check selected." }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot "scripts\media\verify-demo-assets.ps1") -Profile C -Json *> (Join-Path $runRoot "assets.log")
    $assetsOk = $LASTEXITCODE -eq 0
    Add-Check "profile_c_assets" $assetsOk "Generated local Profile C sources are available."
    if (-not $assetsOk) { throw "Profile C asset verification failed." }

    # Do not redirect this startup command: on Windows the managed services
    # intentionally outlive the launcher until the smoke and stop gates run,
    # and inherited redirected handles can otherwise keep the caller waiting.
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot "scripts\media\prepare-recording.ps1") -Profile C -NoBrowser
    $started = $LASTEXITCODE -eq 0
    [IO.File]::WriteAllText((Join-Path $runRoot "startup.log"), "Console streamed to caller; service logs are under .runtime/logs and recording status is under .runtime/recording.")
    Add-Check "profile_c_start" $started "Managed local backend/frontend started without dependency download."
    if (-not $started) { throw "Offline Profile C startup failed." }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot "scripts\smoke-demo.ps1") -Extended *> (Join-Path $runRoot "smoke.log")
    $smokeOk = $LASTEXITCODE -eq 0
    Add-Check "profile_c_smoke" $smokeOk "Liveness, readiness, Memory, Agent, sessions, device stats and insights verified."
    if (-not $smokeOk) { throw "Offline Profile C smoke failed." }
    $status = "PASS"
} catch {
    $errorMessage = $_.Exception.Message
} finally {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot "scripts\stop-demo.ps1") -Force *> (Join-Path $runRoot "stop.log")
    $stopOk = $LASTEXITCODE -eq 0
    Add-Check "managed_stop" $stopOk "SceneMind-owned processes were stopped using verified PID metadata."
    if (-not $stopOk) { $status = "FAIL"; if (-not $errorMessage) { $errorMessage = "Managed stop failed." } }
    if ($null -eq $savedPipNoIndex) { Remove-Item Env:PIP_NO_INDEX -ErrorAction SilentlyContinue } else { $env:PIP_NO_INDEX = $savedPipNoIndex }
    if ($null -eq $savedNpmOffline) { Remove-Item Env:npm_config_offline -ErrorAction SilentlyContinue } else { $env:npm_config_offline = $savedNpmOffline }
}

$payload = [pscustomobject]@{
    run_id = $runId
    ok = $status -eq "PASS" -and @($checks | Where-Object { -not $_.passed }).Count -eq 0
    status = $status
    version = $Version
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    network_configuration_modified = $false
    checks = @($checks | ForEach-Object { $_ })
    error = $errorMessage
    profile_a = "NOT RUN: requires local YOLO weight, approved competition camera, browser permission and trusted HTTPS for phone access."
    profile_b = "NOT RUN: requires local YOLO weight plus at least five approved real images and asset-approval.json."
    profile_c = if ($status -eq "PASS") { "PASS: generated Mock emergency flow; not detector evidence." } else { "FAIL: inspect runtime logs." }
}
$summaryPath = Join-Path $runRoot "summary.json"
$payload | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
if ($Json) { $payload | ConvertTo-Json -Depth 7 } else { foreach ($check in $checks) { Write-Host ("[{0}] {1} - {2}" -f $(if ($check.passed) { "PASS" } else { "FAIL" }), $check.name, $check.detail) }; Write-Host "Offline summary: $summaryPath" }
if (-not $payload.ok) { exit 1 }
