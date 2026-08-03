[CmdletBinding()]
param(
    [ValidateSet("all", "detection", "relation", "memory", "agent", "session")]
    [string]$Module = "all",
    [ValidateSet("mock", "yolo")]
    [string]$AnalyzerMode = "mock",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { throw "Missing .venv. Run .\scripts\setup.ps1 first." }

$runId = "{0}-{1}-{2}" -f (Get-Date -Format "yyyyMMdd-HHmmss"), $AnalyzerMode, $PID
$outputRoot = Join-Path (Get-SceneMindRuntimeRoot) "evaluation\$runId"
New-Item -ItemType Directory -Path (Join-Path $outputRoot "charts") -Force | Out-Null

function Invoke-EvaluationPython {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    if ($Json) { & $python @Arguments | Out-Null } else { & $python @Arguments }
    if ($LASTEXITCODE -ne 0) { throw "Evaluation command failed: python $($Arguments -join ' ')" }
}

Push-Location $projectRoot
try {
    Invoke-EvaluationPython @("-m", "evaluation.scripts.validate_manifest")
    Invoke-EvaluationPython @("-m", "evaluation.scripts.capture_environment", "--analyzer-mode", $AnalyzerMode, "--output", (Join-Path $outputRoot "environment.json"))
    $modules = if ($Module -eq "all") { @("detection", "relation", "memory", "agent", "session") } else { @($Module) }
    foreach ($name in $modules) {
        $output = Join-Path $outputRoot "$name-results.json"
        switch ($name) {
            "detection" { Invoke-EvaluationPython @("-m", "evaluation.scripts.run_detection_eval", "--analyzer-mode", $AnalyzerMode, "--output", $output) }
            "relation" { Invoke-EvaluationPython @("-m", "evaluation.scripts.run_relation_eval", "--analyzer-mode", $AnalyzerMode, "--output", $output) }
            "memory" { Invoke-EvaluationPython @("-m", "evaluation.scripts.run_memory_eval", "--output", $output) }
            "agent" { Invoke-EvaluationPython @("-m", "evaluation.scripts.run_agent_eval", "--output", $output) }
            "session" { Invoke-EvaluationPython @("-m", "evaluation.scripts.run_session_eval", "--output", $output) }
        }
    }
    Copy-Item -LiteralPath (Join-Path $projectRoot "evaluation\manifests\failure_cases.csv") -Destination (Join-Path $outputRoot "failures.csv")
    Invoke-EvaluationPython @("-m", "evaluation.scripts.build_report", "--input-dir", $outputRoot)
} finally {
    Pop-Location
}

$summary = Get-Content -LiteralPath (Join-Path $outputRoot "summary.json") -Raw -Encoding UTF8
if ($Json) { $summary } else {
    Write-Host "Evaluation complete: $outputRoot" -ForegroundColor Green
    $summary | ConvertFrom-Json | ConvertTo-Json -Depth 8
}
