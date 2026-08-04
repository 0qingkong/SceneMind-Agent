[CmdletBinding()]
param(
    [string]$Version = "0.9.0-rc1",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$versionPath = Join-Path $projectRoot "VERSION"
if (-not (Test-Path -LiteralPath $versionPath)) { throw "VERSION is missing; finish version synchronization before packaging." }
$declaredVersion = ([IO.File]::ReadAllText($versionPath, [Text.Encoding]::UTF8)).Trim()
if ($declaredVersion -ne $Version) { throw "Requested version $Version does not match VERSION $declaredVersion." }

& git -C $projectRoot diff --quiet
if ($LASTEXITCODE -ne 0) { throw "Tracked working-tree changes exist; commit them before packaging." }
& git -C $projectRoot diff --cached --quiet
if ($LASTEXITCODE -ne 0) { throw "Staged changes exist; commit them before packaging." }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "scan-sensitive-data.ps1") *> $null
if ($LASTEXITCODE -ne 0) { throw "Sensitive-data/artifact scan failed; packaging stopped." }

$releaseRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot ".runtime\release"))
$packageName = "SceneMind-v$Version"
$packageRoot = [IO.Path]::GetFullPath((Join-Path $releaseRoot $packageName))
if ((Split-Path -Parent $packageRoot) -ne $releaseRoot -or (Split-Path -Leaf $packageRoot) -ne $packageName) { throw "Resolved package target is outside the expected release root." }
if (Test-Path -LiteralPath $packageRoot) {
    if (-not $Force) { throw "Package already exists: $packageRoot. Use -Force only to rebuild this exact generated target." }
    Remove-Item -LiteralPath $packageRoot -Recurse -Force
}
foreach ($name in @("source-code", "docs", "scripts", "evaluation", "sample-data", "presentation", "video")) {
    New-Item -ItemType Directory -Path (Join-Path $packageRoot $name) -Force | Out-Null
}

function Copy-PackageFile([string]$Source, [string]$Destination) {
    $target = [IO.Path]::GetFullPath($Destination)
    if (-not $target.StartsWith($packageRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Package copy escaped target root: $target" }
    $parent = Split-Path -Parent $target
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    [IO.File]::Copy([IO.Path]::GetFullPath($Source), $target, $true)
}

$tracked = @(& git -C $projectRoot ls-files)
foreach ($relative in $tracked) {
    $source = Join-Path $projectRoot $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Tracked source file is missing: $relative" }
    $normalized = $relative.Replace("\", "/")
    Copy-PackageFile $source (Join-Path (Join-Path $packageRoot "source-code") $normalized)
    if ($normalized.StartsWith("docs/")) {
        $destination = Join-Path (Join-Path $packageRoot "docs") $normalized.Substring(5)
    } elseif ($normalized.StartsWith("scripts/")) {
        $destination = Join-Path (Join-Path $packageRoot "scripts") $normalized.Substring(8)
    } elseif ($normalized.StartsWith("presentation/")) {
        $destination = Join-Path (Join-Path $packageRoot "presentation") $normalized.Substring(13)
    } else {
        $destination = ""
    }
    if ($destination) { Copy-PackageFile $source $destination }
}

$evaluationSources = @(
    "docs\EVALUATION.md", "docs\TEST_REPORT.md", "docs\COMPETITION_SUMMARY.md",
    "docs\reports\evaluation-latest.md", "docs\reports\evaluation-latest.json"
)
foreach ($relative in $evaluationSources) {
    $source = Join-Path $projectRoot $relative
    if (Test-Path -LiteralPath $source -PathType Leaf) { Copy-PackageFile $source (Join-Path (Join-Path $packageRoot "evaluation") ([IO.Path]::GetFileName($relative))) }
}
$evaluationCode = @($tracked | Where-Object { $_.Replace("\", "/").StartsWith("backend/evaluation/") })
foreach ($relative in $evaluationCode) {
    $suffix = $relative.Replace("\", "/").Substring("backend/evaluation/".Length)
    Copy-PackageFile (Join-Path $projectRoot $relative) (Join-Path (Join-Path $packageRoot "evaluation\runner-source") $suffix)
}

$utf8 = New-Object Text.UTF8Encoding($false)
$startHere = @'
# START HERE

1. Read `README_OFFLINE.md` and `docs/release/OFFLINE_DELIVERY_GUIDE.md`.
2. Verify `CHECKSUMS.sha256` with `scripts/release/verify-release.ps1` from the original repository.
3. Copy `source-code/` to a writable local directory.
4. Use the existing local Python/Node dependencies or run setup only when network/package mirrors are intentionally available.
5. Start `Profile C` for the deterministic offline emergency demo.

No model weight, private image, user database or final video is bundled automatically.
'@
$offlineReadme = @'
# SceneMind offline release candidate

This package is a clean tracked source snapshot plus documentation, scripts, evaluation evidence and presentation sources. It excludes `.env`, runtime data, uploads, dependency directories, model weights, recordings and unapproved media.

Profile C works after local dependencies are present and uses generated, visibly labeled Mock evidence. Profile B additionally requires approved real images and a user-supplied YOLO weight placed in `source-code/backend/yolo26n.pt` (or configured with `YOLO_MODEL`). Profile A additionally requires approved camera hardware, browser permission and a trusted HTTPS context for a physical phone.

The repository has not supplied a unified source-code redistribution license. Human license and distribution approval is required before external delivery.
'@
[IO.File]::WriteAllText((Join-Path $packageRoot "START_HERE.md"), $startHere.Trim() + "`n", $utf8)
[IO.File]::WriteAllText((Join-Path $packageRoot "README_OFFLINE.md"), $offlineReadme.Trim() + "`n", $utf8)
[IO.File]::WriteAllText((Join-Path $packageRoot "VERSION"), $Version + "`n", $utf8)
[IO.File]::WriteAllText((Join-Path $packageRoot "sample-data\README.md"), "# Sample data`n`nNo private or unclear-license image is bundled. Profile C generates its scenes at runtime. Profile B assets remain local and require asset-approval.json.`n", $utf8)
[IO.File]::WriteAllText((Join-Path $packageRoot "video\README.md"), "# Video`n`nFinal video: NOT INCLUDED. Add it only after human privacy, subtitle, voice-over, playback and redistribution approval; regenerate checksums afterward.`n", $utf8)

$commit = (& git -C $projectRoot rev-parse HEAD).Trim()
$manifest = [ordered]@{
    app_version = $Version
    source_commit_sha = $commit
    build_date_time_utc = [DateTime]::UtcNow.ToString("o")
    package_name = $packageName
    included_components = @("clean tracked source", "documentation", "operator scripts", "evaluation evidence", "presentation sources", "generated Profile C instructions")
    required_local_external_files = @(
        @{ item = "YOLO model weight"; required_for = "Profiles A/B"; included = $false; placement = "source-code/backend/yolo26n.pt or YOLO_MODEL"; checksum = "human-supplied" },
        @{ item = "approved real scene images and asset-approval.json"; required_for = "Profile B"; included = $false; placement = ".runtime/demo-assets/profile-b"; checksum = "human-supplied" },
        @{ item = "browser camera and trusted HTTPS"; required_for = "Profile A/physical phone"; included = $false; placement = "competition environment"; checksum = "not applicable" }
    )
    evaluation_report_paths = @("evaluation/EVALUATION.md", "evaluation/TEST_REPORT.md", "evaluation/evaluation-latest.md", "evaluation/evaluation-latest.json")
    known_issues = @("docs/release/KNOWN_ISSUES.md", "Profile A/B/phone/media gates require human validation", "No unified repository redistribution license is supplied")
    supported_demo_profiles = @(
        @{ profile = "A"; status = "human hardware validation required" },
        @{ profile = "B"; status = "human asset and real-YOLO validation required" },
        @{ profile = "C"; status = "deterministic local emergency path" }
    )
    checksums_file_path = "CHECKSUMS.sha256"
    exclusions = @(".git", ".env", ".runtime", ".venv", "node_modules", "frontend/dist", "databases", "uploads", "model weights", "private media", "logs")
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $packageRoot "MANIFEST.json") -Encoding UTF8
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "generate-checksums.ps1") -PackagePath $packageRoot
if ($LASTEXITCODE -ne 0) { throw "Checksum generation failed." }
Write-Host "Built offline release directory: $packageRoot" -ForegroundColor Green
