[CmdletBinding()]
param(
    [ValidateSet("B", "C")][string]$Profile = "C",
    [switch]$Promote,
    [switch]$ConfirmSelection
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "..\lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
if ($Promote -and -not $ConfirmSelection) {
    throw "Promotion requires -ConfirmSelection after a human privacy/content review of every staged screenshot."
}

$runId = "screens-{0}-{1}" -f $Profile.ToLowerInvariant(), (Get-Date -Format "yyyyMMdd-HHmmss")
$stageRoot = Join-Path $projectRoot (Join-Path ".runtime\recording" $runId)
$screenRoot = Join-Path $stageRoot "screens"
New-Item -ItemType Directory -Path $screenRoot -Force | Out-Null
$statusPath = Join-Path $stageRoot "capture-status.json"
$previous = @{}

try {
    & (Join-Path $PSScriptRoot "prepare-recording.ps1") -Profile $Profile -NoBrowser
    if ($LASTEXITCODE -ne 0) { throw "Recording preflight failed." }

    $observationResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/observations?limit=1" -TimeoutSec 10
    if (@($observationResponse.items).Count -lt 1) { throw "No observation is available for deterministic screenshot setup." }
    $imageUrl = [string]$observationResponse.items[0].image_url
    if ($imageUrl.StartsWith("/")) { $imageUrl = "http://127.0.0.1:8000$imageUrl" }
    $imagePath = Join-Path $stageRoot "permitted-demo.png"
    Invoke-WebRequest -Uri $imageUrl -OutFile $imagePath -UseBasicParsing -TimeoutSec 15

    $variables = [ordered]@{
        SCENEMIND_E2E_BASE_URL = "http://127.0.0.1:5173"
        SCENEMIND_E2E_API_URL = "http://127.0.0.1:8000/api/v1"
        SCENEMIND_E2E_IMAGE = $imagePath
        SCENEMIND_UI_REVIEW_DIR = $screenRoot
        SCENEMIND_E2E_REPORT = (Join-Path $stageRoot "playwright-report.json")
        SCENEMIND_E2E_OUTPUT = (Join-Path $stageRoot "playwright-artifacts")
    }
    foreach ($name in $variables.Keys) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
        [Environment]::SetEnvironmentVariable($name, [string]$variables[$name], "Process")
    }

    Push-Location (Join-Path $projectRoot "frontend")
    try {
        & npm.cmd run test:e2e -- ui-review.spec.ts
        if ($LASTEXITCODE -ne 0) { throw "Playwright screenshot workflow failed. No screenshots were fabricated." }
    } finally { Pop-Location }

    $expectedNames = @(
        "01-home.png", "02-live-lens.png", "03-analysis.png", "04-memory.png",
        "05-observation-evidence.png", "06-agent-evidence.png", "07-session-timeline.png",
        "08-devices.png", "09-glasses-simulator.png", "10-insights.png", "11-privacy.png", "12-system.png"
    )
    $missing = New-Object System.Collections.Generic.List[string]
    foreach ($viewport in @("desktop", "mobile")) {
        foreach ($name in $expectedNames) {
            if (-not (Test-Path -LiteralPath (Join-Path (Join-Path $screenRoot $viewport) $name))) { $missing.Add("$viewport/$name") }
        }
    }
    if ($missing.Count -gt 0) { throw "Missing expected screenshot(s): $($missing -join ', ')" }

    $promoted = New-Object System.Collections.Generic.List[string]
    if ($Promote) {
        $destination = Join-Path $projectRoot "presentation\screenshots"
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
        foreach ($viewport in @("desktop", "mobile")) {
            foreach ($name in $expectedNames) {
                $targetName = "$viewport-$name"
                Copy-Item -LiteralPath (Join-Path (Join-Path $screenRoot $viewport) $name) -Destination (Join-Path $destination $targetName) -Force
                $promoted.Add($targetName)
            }
        }
    }

    [ordered]@{
        run_id = $runId
        status = "PASS"
        profile = $Profile
        staging_directory = $screenRoot
        viewports = @("desktop 1440x900", "mobile 390x844")
        screenshot_count = 24
        promoted = @($promoted | ForEach-Object { $_ })
        human_review = if ($Promote) { "Explicit selection supplied; final publication approval still required." } else { "NOT RUN: review privacy/content, then rerun with -Promote -ConfirmSelection." }
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statusPath -Encoding UTF8
    Write-Host "Captured 24 deterministic screenshots in ignored staging: $screenRoot" -ForegroundColor Green
    if (-not $Promote) { Write-Host "Promotion NOT RUN. Human review is required first." -ForegroundColor Yellow }
} catch {
    [ordered]@{ run_id = $runId; status = "FAIL"; profile = $Profile; error = $_.Exception.Message; fabricated = $false } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statusPath -Encoding UTF8
    throw
} finally {
    foreach ($name in $previous.Keys) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], "Process")
    }
}
