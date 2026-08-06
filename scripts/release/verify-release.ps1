[CmdletBinding()]
param(
    [string]$Version = "0.9.0-rc1",
    [string]$PackagePath = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if (-not $PackagePath) { $PackagePath = Join-Path $projectRoot ".runtime\release\SceneMind-v$Version" }
$sourceRoot = [IO.Path]::GetFullPath($PackagePath)
if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) { throw "Release package directory not found: $sourceRoot" }
$tempBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$inspectionRoot = Join-Path $tempBase ("scenemind-release-verify-" + [Guid]::NewGuid().ToString("N"))
$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$Name, [bool]$Passed, [string]$Detail) { $checks.Add([pscustomobject]@{ name = $Name; passed = $Passed; detail = $Detail }) }

try {
    New-Item -ItemType Directory -Path $inspectionRoot -Force | Out-Null
    Copy-Item -Path (Join-Path $sourceRoot "*") -Destination $inspectionRoot -Recurse -Force
    Add-Check "clean_temp_inspection" $true "Copied package into isolated temporary inspection directory."

    $required = @("source-code", "docs", "scripts", "evaluation", "sample-data", "presentation", "video", "START_HERE.md", "README_OFFLINE.md", "VERSION", "MANIFEST.json", "CHECKSUMS.sha256")
    $missing = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $inspectionRoot $_)) })
    Add-Check "required_tree" ($missing.Count -eq 0) $(if ($missing.Count) { "Missing: $($missing -join ', ')" } else { "$($required.Count) required entries found." })

    $checksumPath = Join-Path $inspectionRoot "CHECKSUMS.sha256"
    $checksumFailures = New-Object System.Collections.Generic.List[string]
    if (Test-Path -LiteralPath $checksumPath) {
        foreach ($line in Get-Content -LiteralPath $checksumPath -Encoding UTF8) {
            if (-not $line.Trim()) { continue }
            if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') { $checksumFailures.Add("invalid checksum line"); continue }
            $expected = $Matches[1].ToLowerInvariant()
            $relative = $Matches[2].Replace("/", [IO.Path]::DirectorySeparatorChar)
            $candidate = [IO.Path]::GetFullPath((Join-Path $inspectionRoot $relative))
            if (-not $candidate.StartsWith($inspectionRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { $checksumFailures.Add("unsafe path redacted"); continue }
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { $checksumFailures.Add("missing $($Matches[2])"); continue }
            $actual = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actual -ne $expected) { $checksumFailures.Add("mismatch $($Matches[2])") }
        }
    } else { $checksumFailures.Add("CHECKSUMS.sha256 missing") }
    Add-Check "sha256" ($checksumFailures.Count -eq 0) $(if ($checksumFailures.Count) { $checksumFailures -join '; ' } else { "All listed package files match SHA-256." })

    $forbidden = New-Object System.Collections.Generic.List[string]
    foreach ($file in Get-ChildItem -LiteralPath $inspectionRoot -Recurse -File) {
        $relative = $file.FullName.Substring($inspectionRoot.Length + 1).Replace("\", "/")
        $extension = $file.Extension.ToLowerInvariant()
        if ($file.Name -eq ".env" -or $extension -in @(".pt", ".onnx", ".db", ".sqlite", ".sqlite3", ".log", ".mp4", ".mov", ".webm")) { $forbidden.Add($relative) }
        if ($relative -match '(^|/)(\.git|\.runtime|\.venv|node_modules|runs)(/|$)' -or $relative -match '(^|/)frontend/dist(/|$)') { $forbidden.Add($relative) }
    }
    Add-Check "forbidden_artifacts" ($forbidden.Count -eq 0) $(if ($forbidden.Count) { "Forbidden paths: $($forbidden -join ', ')" } else { "No secret/runtime/dependency/model/database/recording artifacts found." })

    $declared = if (Test-Path -LiteralPath (Join-Path $inspectionRoot "VERSION")) { (Get-Content -LiteralPath (Join-Path $inspectionRoot "VERSION") -Raw).Trim() } else { "" }
    $manifest = if (Test-Path -LiteralPath (Join-Path $inspectionRoot "MANIFEST.json")) { Get-Content -LiteralPath (Join-Path $inspectionRoot "MANIFEST.json") -Raw | ConvertFrom-Json } else { $null }
    $packageJsonPath = Join-Path $inspectionRoot "source-code\frontend\package.json"
    $packageJson = if (Test-Path -LiteralPath $packageJsonPath) { Get-Content -LiteralPath $packageJsonPath -Raw | ConvertFrom-Json } else { $null }
    $versionOk = $declared -eq $Version -and $manifest -and $manifest.app_version -eq $Version -and $packageJson -and $packageJson.version -eq $Version
    Add-Check "static_version_config" $versionOk "Root VERSION, manifest and frontend package must equal $Version."

    $external = if ($manifest) { @($manifest.required_local_external_files) } else { @() }
    $externalOk = $external.Count -ge 3 -and @($external | Where-Object { $_.included -eq $true }).Count -eq 0
    Add-Check "external_asset_manifest" $externalOk "Weights, Profile B images and camera/HTTPS requirements must be explicit and not silently bundled."

    $failed = @($checks | Where-Object { -not $_.passed })
    $payload = [pscustomobject]@{
        ok = $failed.Count -eq 0
        version = $Version
        package_path = $sourceRoot
        inspected_at_utc = [DateTime]::UtcNow.ToString("o")
        checks = @($checks | ForEach-Object { $_ })
        packaged_smoke = "Static package verification complete; deterministic runtime smoke is delegated to offline-check.ps1 using installed local dependencies."
    }
    if ($Json) { $payload | ConvertTo-Json -Depth 7 } else { foreach ($check in $checks) { Write-Host ("[{0}] {1} - {2}" -f $(if ($check.passed) { "PASS" } else { "FAIL" }), $check.name, $check.detail) } }
    if ($failed.Count -gt 0) { exit 1 }
} finally {
    $resolvedInspection = [IO.Path]::GetFullPath($inspectionRoot)
    if ($resolvedInspection.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $resolvedInspection).StartsWith("scenemind-release-verify-")) {
        Remove-Item -LiteralPath $resolvedInspection -Recurse -Force -ErrorAction SilentlyContinue
    }
}
