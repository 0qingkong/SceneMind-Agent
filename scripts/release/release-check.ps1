[CmdletBinding()]
param(
    [string]$Version = "0.9.0-rc1",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$runtimeRoot = Join-Path $projectRoot ".runtime"
if (-not (Test-Path -LiteralPath $runtimeRoot)) { New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null }
$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$Name, [bool]$Passed, [string]$Detail) {
    $checks.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail })
}
function Read-Text([string]$Relative) {
    $path = Join-Path $projectRoot $Relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return "" }
    return [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
}

$required = @(
    "VERSION", "CHANGELOG.md", "README.md", "docs\PROJECT_STATE.md",
    "docs\demo\FINAL_DEMO_SCRIPT.md", "docs\demo\CLAIMS_LEDGER_FINAL.md",
    "docs\release\RELEASE_CHECKLIST.md", "docs\release\RELEASE_NOTES_v0.9.0-rc1.md",
    "docs\release\KNOWN_ISSUES.md", "docs\release\RELEASE_FREEZE_POLICY.md",
    "docs\release\OFFLINE_DELIVERY_GUIDE.md"
)
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $projectRoot $_) -PathType Leaf) })
Add-Check "required_release_files" ($missing.Count -eq 0) $(if ($missing.Count) { "Missing: $($missing -join ', ')" } else { "$($required.Count) files present." })

$declared = (Read-Text "VERSION").Trim()
$package = if (Test-Path -LiteralPath (Join-Path $projectRoot "frontend\package.json")) { Get-Content -LiteralPath (Join-Path $projectRoot "frontend\package.json") -Raw | ConvertFrom-Json } else { $null }
$backendVersion = Read-Text "backend\app\core\version.py"
$systemStrip = Read-Text "frontend\src\components\system\GlobalSystemStrip.vue"
$versionOk = $declared -eq $Version -and $package -and $package.version -eq $Version -and
    $backendVersion -match ('APP_VERSION\s*=\s*"' + [regex]::Escape($Version) + '"') -and
    $systemStrip -match ('v' + [regex]::Escape($Version))
Add-Check "version_consistency" $versionOk "Expected VERSION, backend, frontend package and UI chip to equal $Version."

$routes = @("/live", "/analyze", "/memory", "/agent", "/sessions", "/devices", "/glasses", "/insights", "/privacy", "/system")
$router = Read-Text "frontend\src\router\index.ts"
$demoScript = Read-Text "docs\demo\FINAL_DEMO_SCRIPT.md"
$routeFailures = @($routes | Where-Object { $router -notmatch [regex]::Escape($_) -or $demoScript -notmatch [regex]::Escape($_) })
Add-Check "navigation_and_demo_routes" ($routeFailures.Count -eq 0) $(if ($routeFailures.Count) { "Route mismatch: $($routeFailures -join ', ')" } else { "$($routes.Count) routes match router and demo script." })

$glasses = Read-Text "frontend\src\views\GlassesView.vue"
$simulatorOk = $glasses -match 'AI Glasses Simulator' -and $glasses -match '\u4E0D\u4EE3\u8868\u5DF2\u8FDE\u63A5\u771F\u5B9E AI \u773C\u955C\u786C\u4EF6'
Add-Check "simulator_disclaimer" $simulatorOk "Exact simulator name and not-real-hardware disclosure must be visible."

$profileFiles = @("README.md", "docs\DEMO_RUNBOOK.md", "docs\demo\FINAL_DEMO_SCRIPT.md", "docs\release\OFFLINE_DELIVERY_GUIDE.md")
$profileFailures = @($profileFiles | Where-Object { $text = Read-Text $_; $text -notmatch 'Profile A' -or $text -notmatch 'Profile B' -or $text -notmatch 'Profile C' })
Add-Check "profile_definitions" ($profileFailures.Count -eq 0) $(if ($profileFailures.Count) { "Incomplete A/B/C wording: $($profileFailures -join ', ')" } else { "A/B/C present in operator documents." })

$metricFiles = @("README.md", "docs\EVALUATION.md", "docs\competition\PITCH_DECK.md", "docs\competition\TECHNICAL_REPORT.md", "docs\demo\CLAIMS_LEDGER_FINAL.md", "docs\release\RELEASE_NOTES_v0.9.0-rc1.md")
$metricPatterns = @('10\s*/\s*10', '17\s*/\s*18', '11\s*/\s*12', '6\s*/\s*6')
$metricFailures = New-Object System.Collections.Generic.List[string]
foreach ($file in $metricFiles) {
    $text = Read-Text $file
    foreach ($pattern in $metricPatterns) { if ($text -notmatch $pattern) { $metricFailures.Add("${file}:$pattern") } }
}
Add-Check "day15_metrics" ($metricFailures.Count -eq 0) $(if ($metricFailures.Count) { $metricFailures -join '; ' } else { "Day 15 metrics match all public sources." })

$claims = (Read-Text "README.md") + (Read-Text "docs\competition\TECHNICAL_REPORT.md") + (Read-Text "docs\demo\FINAL_DEMO_SCRIPT.md") + (Read-Text "docs\release\RELEASE_NOTES_v0.9.0-rc1.md")
$boundariesOk = $claims -match 'same physical|physical-instance|\u540C\u4E00.*\u73B0\u5B9E' -and $claims -match 'depth|\u6DF1\u5EA6' -and $claims -match 'not real hardware|not connected eyewear|\u4E0D.*\u771F\u5B9E.*\u786C\u4EF6'
Add-Check "truthful_boundaries" $boundariesOk "Identity, depth and simulated-glasses limits must remain in public sources."

$docChecker = Join-Path $projectRoot "scripts\check-release-docs.ps1"
if (Test-Path -LiteralPath $docChecker) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $docChecker -Json *> (Join-Path $runtimeRoot "release-doc-check.log")
    Add-Check "document_links_and_hygiene" ($LASTEXITCODE -eq 0) "Delegated to scripts/check-release-docs.ps1."
} else { Add-Check "document_links_and_hygiene" $false "Documentation checker is missing." }

$failed = @($checks | Where-Object { -not $_.passed })
$payload = [pscustomobject]@{ ok = $failed.Count -eq 0; version = $Version; checked_at_utc = [DateTime]::UtcNow.ToString("o"); checks = @($checks | ForEach-Object { $_ }) }
if ($Json) { $payload | ConvertTo-Json -Depth 6 } else {
    foreach ($check in $checks) { Write-Host ("[{0}] {1} - {2}" -f $(if ($check.passed) { "PASS" } else { "FAIL" }), $check.name, $check.detail) }
}
if ($failed.Count -gt 0) { exit 1 }
