[CmdletBinding()]
param(
    [switch]$SkipBrowser,
    [ValidateSet("C")][string]$Profile = "C",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$runId = "bug-bash-{0}-{1}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $PID
$runRoot = Join-Path $projectRoot (Join-Path ".runtime\release" $runId)
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null
$results = New-Object System.Collections.Generic.List[object]

function Invoke-GateProcess([string]$Name, [string]$FilePath, [string[]]$Arguments, [string]$WorkingDirectory = $projectRoot, [bool]$CaptureOutput = $true) {
    $stdout = Join-Path $runRoot "$Name.stdout.log"
    $stderr = Join-Path $runRoot "$Name.stderr.log"
    $started = [DateTime]::UtcNow
    try {
        Push-Location $WorkingDirectory
        try {
            $savedPreference = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            if ($CaptureOutput) {
                & $FilePath @Arguments 1> $stdout 2> $stderr
            } else {
                # A startup command intentionally leaves managed services alive
                # for the following smoke gate. Redirecting its console handles
                # can keep the parent waiting on those descendants on Windows.
                & $FilePath @Arguments
                [IO.File]::WriteAllText($stdout, "Console streamed to the bug-bash runner; see .runtime/logs and recording status JSON.")
                [IO.File]::WriteAllText($stderr, "")
            }
            $code = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $savedPreference
            Pop-Location
        }
        $detail = if ($code -eq 0) { "Command passed." } else { "Exit code $code; inspect $stderr and $stdout." }
    } catch {
        $code = 999
        $detail = "Unable to run command: $($_.Exception.Message)"
    }
    $duration = [Math]::Round(([DateTime]::UtcNow - $started).TotalSeconds, 2)
    $results.Add([pscustomobject]@{ name = $Name; passed = $code -eq 0; exit_code = $code; duration_seconds = $duration; detail = $detail; stdout = $stdout; stderr = $stderr })
    if (-not $Json) { Write-Host ("[{0}] {1} ({2}s) - {3}" -f $(if ($code -eq 0) { "PASS" } else { "FAIL" }), $Name, $duration, $detail) }
}

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$npm = (Get-Command npm.cmd -ErrorAction SilentlyContinue)
if (-not (Test-Path -LiteralPath $python)) { throw "Missing .venv; run scripts/setup.ps1 first." }
if (-not $npm) { throw "npm.cmd is required." }
$powershell = (Get-Command powershell.exe -ErrorAction Stop).Source

Invoke-GateProcess "backend_pytest" $python @("-m", "pytest", "tests", "-q", "--basetemp", (Join-Path $runRoot "pytest"), "-p", "no:cacheprovider") (Join-Path $projectRoot "backend")
Invoke-GateProcess "frontend_build" $npm.Source @("run", "build") (Join-Path $projectRoot "frontend")
Invoke-GateProcess "frontend_capture_tests" $npm.Source @("run", "test:capture") (Join-Path $projectRoot "frontend")

$e2eArguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\e2e-test.ps1"))
if ($SkipBrowser) { $e2eArguments += "-SkipBrowser" }
Invoke-GateProcess "day14_e2e" $powershell $e2eArguments
Invoke-GateProcess "failure_injection" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\failure-test.ps1"))
Invoke-GateProcess "data_integrity" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\data-integrity-test.ps1"))

Invoke-GateProcess "profile_c_prepare" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\media\prepare-recording.ps1"), "-Profile", $Profile, "-NoBrowser") $projectRoot $false
Invoke-GateProcess "profile_c_extended_smoke" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\smoke-demo.ps1"), "-Extended")
Invoke-GateProcess "profile_c_stop" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\stop-demo.ps1"), "-Force")

Invoke-GateProcess "release_consistency" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\release\release-check.ps1"), "-Version", "0.9.0-rc1", "-Json")
Invoke-GateProcess "sensitive_data" $powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts\release\scan-sensitive-data.ps1"), "-OutputPath", (Join-Path $runRoot "sensitive-data.json"), "-Json")

$failed = @($results | Where-Object { -not $_.passed })
$summary = [pscustomobject]@{
    run_id = $runId
    version = "0.9.0-rc1"
    profile = $Profile
    browser_skipped = [bool]$SkipBrowser
    ok = $failed.Count -eq 0
    started_artifacts = $runRoot
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    automated_results = @($results | ForEach-Object { $_ })
    open_p0 = 0
    open_p1 = 0
    human_gates = @(
        "Profile A competition camera: NOT RUN",
        "Profile B approved real-YOLO images: NOT RUN",
        "Physical phone over HTTPS: NOT RUN",
        "Final media and package inspection: NOT RUN"
    )
}
$summaryPath = Join-Path $runRoot "summary.json"
$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
if ($Json) { $summary | ConvertTo-Json -Depth 8 } else { Write-Host "Bug-bash summary: $summaryPath" }
if ($failed.Count -gt 0) { exit 1 }
