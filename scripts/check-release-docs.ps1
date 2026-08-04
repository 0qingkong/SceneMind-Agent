[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$results = New-Object 'System.Collections.Generic.List[object]'

function Add-Result {
    param([string]$Name, [bool]$Passed, [string]$Detail)
    $results.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail }) | Out-Null
}

function Read-RepoFile {
    param([string]$RelativePath)
    return [System.IO.File]::ReadAllText(
        (Join-Path $repoRoot $RelativePath),
        [System.Text.Encoding]::UTF8
    )
}

$requiredFiles = @(
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/API.md",
    "docs/DEPLOYMENT.md",
    "docs/DEVICE_ADAPTERS.md",
    "docs/PRIVACY.md",
    "docs/EVALUATION.md",
    "docs/TEST_REPORT.md",
    "docs/DEMO_RUNBOOK.md",
    "docs/RECOVERY.md",
    "docs/OFFLINE_PACKAGE.md",
    "docs/LIMITATIONS.md",
    "docs/USER_GUIDE.md",
    "docs/CONTRIBUTING.md",
    "docs/CHANGELOG.md",
    "docs/COMPETITION_SUMMARY.md",
    "docs/competition/PITCH_DECK.md",
    "docs/competition/TECHNICAL_REPORT.md",
    "docs/competition/DEMO_SCRIPT.md",
    "docs/competition/JUDGE_QA.md",
    "docs/competition/CLAIMS_LEDGER.md",
    "docs/competition/SUBMISSION_CHECKLIST.md",
    "docs/competition/SCREENSHOT_PLAN.md"
    "VERSION",
    "CHANGELOG.md",
    "docs/demo/FINAL_DEMO_SCRIPT.md",
    "docs/demo/CLAIMS_LEDGER_FINAL.md",
    "docs/demo/SUBTITLE_SCRIPT.md",
    "docs/release/BUG_BASH_PLAN.md",
    "docs/release/BUG_BASH_REPORT.md",
    "docs/release/RELEASE_CHECKLIST.md",
    "docs/release/RELEASE_NOTES_v0.9.0-rc1.md",
    "docs/release/KNOWN_ISSUES.md",
    "docs/release/RELEASE_FREEZE_POLICY.md",
    "docs/release/OFFLINE_DELIVERY_GUIDE.md"
)

$missingFiles = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $repoRoot $_) -PathType Leaf) })
Add-Result "required_documents" ($missingFiles.Count -eq 0) $(if ($missingFiles.Count) { "Missing: $($missingFiles -join ', ')" } else { "$($requiredFiles.Count) required documents found" })

$trackedMarkdown = @(& git -C $repoRoot ls-files "README.md" "docs/*.md" "docs/**/*.md")
$invalidLinks = New-Object 'System.Collections.Generic.List[string]'
foreach ($relativeFile in $trackedMarkdown) {
    $fullFile = Join-Path $repoRoot $relativeFile
    $sourceDir = Split-Path -Parent $fullFile
    $content = [System.IO.File]::ReadAllText($fullFile, [System.Text.Encoding]::UTF8)
    foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')) {
        $target = $match.Groups[1].Value.Trim().Trim('<', '>')
        if ($target -match '^(https?://|mailto:|#)') { continue }
        $target = ($target -split '#', 2)[0]
        if ([string]::IsNullOrWhiteSpace($target)) { continue }
        $resolvedTarget = Join-Path $sourceDir $target
        if (-not (Test-Path -LiteralPath $resolvedTarget)) {
            $invalidLinks.Add("${relativeFile}: $target") | Out-Null
        }
    }
}
Add-Result "markdown_links" ($invalidLinks.Count -eq 0) $(if ($invalidLinks.Count) { $invalidLinks -join '; ' } else { "$($trackedMarkdown.Count) tracked Markdown files checked" })

$combinedMarkdown = ($trackedMarkdown | ForEach-Object { Read-RepoFile $_ }) -join "`n"
$bannedMatches = @([regex]::Matches($combinedMarkdown, '(?i)\b(TODO|TBD|PLACEHOLDER)\b') | ForEach-Object { $_.Value.ToUpperInvariant() } | Select-Object -Unique)
Add-Result "no_document_placeholders" ($bannedMatches.Count -eq 0) $(if ($bannedMatches.Count) { "Found: $($bannedMatches -join ', ')" } else { "No prohibited completion markers" })

$absolutePathMatches = @([regex]::Matches($combinedMarkdown, '(?i)\b[A-Z]:\\(?:Users|scenemind-agent-starter|tmp)\\[^\s`]+') | ForEach-Object { $_.Value } | Select-Object -Unique)
Add-Result "no_local_absolute_paths" ($absolutePathMatches.Count -eq 0) $(if ($absolutePathMatches.Count) { $absolutePathMatches -join '; ' } else { "No workstation-specific absolute paths" })

$secretMatches = @([regex]::Matches($combinedMarkdown, '(?i)(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,})'))
Add-Result "no_embedded_secrets" ($secretMatches.Count -eq 0) $(if ($secretMatches.Count) { "Potential secret pattern found" } else { "No high-confidence credential pattern" })

$package = Get-Content -Raw -LiteralPath (Join-Path $repoRoot "frontend/package.json") | ConvertFrom-Json
$backendVersionText = Read-RepoFile "backend/app/core/version.py"
$appShellText = Read-RepoFile "frontend/src/App.vue"
$managedStartText = Read-RepoFile "scripts/start-backend.ps1"
$expectedVersion = "0.9.0-rc1"
$expectedBuild = "day19-20-release-candidate"
$versionOk = $package.version -eq $expectedVersion -and
    $backendVersionText -match ('APP_VERSION\s*=\s*"' + [regex]::Escape($expectedVersion) + '"') -and
    $backendVersionText -match ('APP_BUILD\s*=\s*"' + [regex]::Escape($expectedBuild) + '"') -and
    $managedStartText -match ('APP_BUILD\s*=\s*"' + [regex]::Escape($expectedBuild) + '"') -and
    $appShellText -match ('v' + [regex]::Escape($expectedVersion))
Add-Result "version_consistency" $versionOk "Expected version $expectedVersion and build $expectedBuild"

$profileDocs = @("README.md", "docs/DEPLOYMENT.md", "docs/DEMO_RUNBOOK.md", "docs/competition/DEMO_SCRIPT.md", "docs/demo/FINAL_DEMO_SCRIPT.md", "docs/release/OFFLINE_DELIVERY_GUIDE.md")
$profileFailures = @()
foreach ($file in $profileDocs) {
    $text = Read-RepoFile $file
    if ($text -notmatch 'Profile A' -or $text -notmatch 'Profile B' -or $text -notmatch 'Profile C') { $profileFailures += $file }
}
Add-Result "profile_definitions" ($profileFailures.Count -eq 0) $(if ($profileFailures.Count) { "Incomplete A/B/C definitions: $($profileFailures -join ', ')" } else { "Profile A/B/C present in all operator entry points" })

$simulatorPattern = '\u5F53\u524D\u4E3A\u6D4F\u89C8\u5668\u7AEF\u6A21\u62DF\uFF0C\u4E0D\u4EE3\u8868\u5DF2\u8FDE\u63A5\u771F\u5B9E AI \u773C\u955C\u786C\u4EF6\u3002'
$simulatorFiles = @("frontend/src/views/GlassesView.vue", "docs/DEVICE_ADAPTERS.md", "docs/competition/CLAIMS_LEDGER.md", "docs/demo/CLAIMS_LEDGER_FINAL.md")
$simulatorFailures = @($simulatorFiles | Where-Object { (Read-RepoFile $_) -notmatch $simulatorPattern })
$markerText = (Read-RepoFile "README.md") + (Read-RepoFile "docs/COMPETITION_SUMMARY.md") + (Read-RepoFile "docs/competition/CLAIMS_LEDGER.md")
$markersOk = $simulatorFailures.Count -eq 0 -and $markerText -match 'Mock' -and $markerText -match 'Demo' -and $markerText -match 'Simulator'
Add-Result "mock_demo_simulator_markers" $markersOk $(if ($simulatorFailures.Count) { "Missing exact simulator disclosure: $($simulatorFailures -join ', ')" } else { "Mock, Demo and Simulator disclosures are consistent" })

$metricFiles = @("README.md", "docs/EVALUATION.md", "docs/COMPETITION_SUMMARY.md", "docs/competition/PITCH_DECK.md", "docs/competition/TECHNICAL_REPORT.md", "docs/demo/CLAIMS_LEDGER_FINAL.md", "docs/release/RELEASE_NOTES_v0.9.0-rc1.md")
$metricPatterns = @('10\s*/\s*10', '17\s*/\s*18', '11\s*/\s*12', '6\s*/\s*6')
$metricFailures = @()
foreach ($file in $metricFiles) {
    $text = Read-RepoFile $file
    foreach ($pattern in $metricPatterns) {
        if ($text -notmatch $pattern) { $metricFailures += "${file}:$pattern" }
    }
}
Add-Result "day15_metric_consistency" ($metricFailures.Count -eq 0) $(if ($metricFailures.Count) { $metricFailures -join '; ' } else { "Memory, Agent, relation and session baselines match in $($metricFiles.Count) release documents" })

$trackedForbidden = @(& git -C $repoRoot ls-files "*.pt" "*.onnx" "*.db" "*.sqlite" "*.sqlite3" "*.log" "*.mp4" "*.mov" "*.webm")
$trackedRuntime = @(& git -C $repoRoot ls-files ".runtime/**" "artifacts/ui-review/**" "frontend/dist/**" "frontend/node_modules/**" "backend/data/**")
$gitHygieneOk = $trackedForbidden.Count -eq 0 -and $trackedRuntime.Count -eq 0
Add-Result "git_hygiene" $gitHygieneOk $(if (-not $gitHygieneOk) { (@($trackedForbidden) + @($trackedRuntime)) -join '; ' } else { "No forbidden release/runtime artifacts are tracked" })

$failed = @($results | Where-Object { -not $_.passed })
$payload = [pscustomobject]@{
    ok = $failed.Count -eq 0
    checked_at = [DateTime]::UtcNow.ToString("o")
    version = $expectedVersion
    checks = $results
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 5
} else {
    foreach ($result in $results) {
        $status = if ($result.passed) { "PASS" } else { "FAIL" }
        Write-Host ("[{0}] {1} - {2}" -f $status, $result.name, $result.detail)
    }
    Write-Host ("Release documentation check: {0}/{1} passed" -f ($results.Count - $failed.Count), $results.Count)
}

if ($failed.Count -gt 0) { exit 1 }
exit 0
