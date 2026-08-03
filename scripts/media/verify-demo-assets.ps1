[CmdletBinding()]
param(
    [ValidateSet("B", "C")][string]$Profile = "C",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "..\lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$checks = New-Object System.Collections.Generic.List[object]

function Add-AssetCheck([string]$Name, [string]$Status, [string]$Detail) {
    $checks.Add([pscustomobject]@{ name = $Name; status = $Status; detail = $Detail })
}

foreach ($relative in @(
    "docs\DEMO_RUNBOOK.md",
    "docs\TEST_REPORT.md",
    "docs\EVALUATION.md",
    "docs\demo\DEMO_ASSET_MANIFEST.md",
    "docs\demo\FINAL_DEMO_SCRIPT.md"
)) {
    $exists = Test-Path -LiteralPath (Join-Path $projectRoot $relative)
    Add-AssetCheck $relative $(if ($exists) { "PASS" } else { "FAIL" }) $(if ($exists) { "Present." } else { "Required readiness evidence is missing." })
}

if ($Profile -eq "C") {
    foreach ($relative in @("backend\app\services\demo_data.py", "scripts\seed-demo.ps1", "scripts\reset-demo.ps1")) {
        $exists = Test-Path -LiteralPath (Join-Path $projectRoot $relative)
        Add-AssetCheck $relative $(if ($exists) { "PASS" } else { "FAIL" }) $(if ($exists) { "Deterministic local source is present." } else { "Profile C cannot be generated." })
    }
    Add-AssetCheck "Profile C licensing" "PASS" "Scenes are code-generated at runtime; no private or unclear-license image is required."
} else {
    Import-SceneMindEnv
    $modelName = if ($env:YOLO_MODEL) { $env:YOLO_MODEL } else { "yolo26n.pt" }
    $modelCandidates = @((Join-Path $projectRoot $modelName), (Join-Path $projectRoot (Join-Path "backend" $modelName)))
    $model = @($modelCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1)
    Add-AssetCheck "Local YOLO weight" $(if ($model.Count -eq 1) { "PASS" } else { "FAIL" }) $(if ($model.Count -eq 1) { "Present locally; redistribution is not implied." } else { "Place a user-supplied weight locally; setup will not download it." })

    $assetRoot = Join-Path $projectRoot ".runtime\demo-assets\profile-b"
    $approvalPath = Join-Path $assetRoot "asset-approval.json"
    if (-not (Test-Path -LiteralPath $approvalPath)) {
        Add-AssetCheck "Profile B approvals" "FAIL" "Missing ignored .runtime/demo-assets/profile-b/asset-approval.json. Human-approved assets are required."
    } else {
        try {
            $approval = Get-Content -LiteralPath $approvalPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $items = @($approval.assets)
            $missing = @($items | Where-Object { -not $_.filename -or -not $_.sha256 -or -not $_.permission -or -not (Test-Path -LiteralPath (Join-Path $assetRoot ([string]$_.filename))) })
            $valid = $items.Count -ge 5 -and $missing.Count -eq 0
            Add-AssetCheck "Profile B approvals" $(if ($valid) { "PASS" } else { "FAIL" }) $(if ($valid) { "$($items.Count) approved local assets with declared checksums." } else { "Require at least five existing assets with filename, SHA-256 and permission statement." })
        } catch {
            Add-AssetCheck "Profile B approvals" "FAIL" "Approval manifest is invalid JSON or unreadable."
        }
    }
}

$failed = @($checks | Where-Object { $_.status -eq "FAIL" }).Count -gt 0
$result = [pscustomobject]@{
    ok = -not $failed
    profile = $Profile
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    checks = @($checks | ForEach-Object { $_ })
    human_gate = if ($Profile -eq "B") { "Approved real images and their permissions/checksums are required." } else { "No real detector or camera claim may be inferred from Profile C." }
}
if ($Json) { $result | ConvertTo-Json -Depth 6 } else {
    foreach ($item in $checks) {
        $color = if ($item.status -eq "PASS") { "Green" } else { "Red" }
        Write-Host ("{0,-5} {1,-34} {2}" -f $item.status, $item.name, $item.detail) -ForegroundColor $color
    }
    Write-Host $result.human_gate -ForegroundColor Yellow
}
if ($failed) { exit 1 }
