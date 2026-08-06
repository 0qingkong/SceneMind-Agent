[CmdletBinding()]
param(
    [ValidateSet("3min", "5min", "All")][string]$Version = "All",
    [string]$Source = "",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "..\lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
if (-not $Source) { $Source = Join-Path $projectRoot "docs\demo\SUBTITLE_SCRIPT.md" }
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $projectRoot "presentation\subtitles" }
if (-not (Test-Path -LiteralPath $Source)) { throw "Subtitle timing source not found: $Source" }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

function Convert-TimeToMilliseconds([string]$Value) {
    if ($Value -notmatch "^(\d{2}):(\d{2}):(\d{2}),(\d{3})$") { throw "Invalid SRT timestamp: $Value" }
    return (((([int]$Matches[1] * 60) + [int]$Matches[2]) * 60 + [int]$Matches[3]) * 1000 + [int]$Matches[4])
}

function Write-SubtitleVersion([string]$Name, [string]$OutputName) {
    $lines = Get-Content -LiteralPath $Source -Encoding UTF8
    $inSection = $false
    $entries = New-Object System.Collections.Generic.List[object]
    foreach ($line in $lines) {
        if ($line -eq "## $Name timing") { $inSection = $true; continue }
        if ($inSection -and $line.StartsWith("## ")) { break }
        if ($inSection -and $line -match "^\| (\d{2}:\d{2}:\d{2},\d{3}) \| (\d{2}:\d{2}:\d{2},\d{3}) \| (.+) \|$") {
            $entries.Add([pscustomobject]@{ start = $Matches[1]; end = $Matches[2]; text = $Matches[3] })
        }
    }
    if ($entries.Count -eq 0) { throw "No subtitle entries found for $Name." }
    $previousEnd = -1
    $output = New-Object System.Collections.Generic.List[string]
    for ($index = 0; $index -lt $entries.Count; $index++) {
        $entry = $entries[$index]
        $startMs = Convert-TimeToMilliseconds $entry.start
        $endMs = Convert-TimeToMilliseconds $entry.end
        if ($startMs -lt $previousEnd) { throw "Subtitle overlap before block $($index + 1) in $Name." }
        if ($endMs -le $startMs) { throw "Non-positive subtitle duration at block $($index + 1) in $Name." }
        if ([string]$entry.text -match "[\r\n]") { throw "Subtitle block contains an unsupported newline." }
        $output.Add([string]($index + 1))
        $output.Add("$($entry.start) --> $($entry.end)")
        $output.Add([string]$entry.text)
        if ($index -lt $entries.Count - 1) { $output.Add("") }
        $previousEnd = $endMs
    }
    $path = Join-Path $OutputDirectory $OutputName
    $output | Set-Content -LiteralPath $path -Encoding UTF8
    Write-Host "Generated $path ($($entries.Count) blocks)." -ForegroundColor Green
}

if ($Version -in @("3min", "All")) { Write-SubtitleVersion "3-minute" "scenemind-demo-3min.zh-CN.srt" }
if ($Version -in @("5min", "All")) { Write-SubtitleVersion "5-minute" "scenemind-demo-5min.zh-CN.srt" }
