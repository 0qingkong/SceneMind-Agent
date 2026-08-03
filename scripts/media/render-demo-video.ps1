[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ScreenRecording,
    [Parameter(Mandatory = $true)][string]$Voiceover,
    [string]$Subtitles = "",
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "..\lib\common.ps1")
$projectRoot = Get-SceneMindProjectRoot
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) { throw "FFmpeg is not available. Install/approve it separately; this script never downloads it." }
foreach ($inputPath in @($ScreenRecording, $Voiceover)) {
    if (-not (Test-Path -LiteralPath $inputPath -PathType Leaf)) { throw "Input media not found: $inputPath" }
}
if ($Subtitles -and -not (Test-Path -LiteralPath $Subtitles -PathType Leaf)) { throw "Subtitle file not found: $Subtitles" }
$resolvedInputs = @([IO.Path]::GetFullPath($ScreenRecording), [IO.Path]::GetFullPath($Voiceover))
$resolvedOutput = [IO.Path]::GetFullPath($Output)
if ($resolvedOutput -in $resolvedInputs) { throw "Output must differ from every original input." }
if (Test-Path -LiteralPath $resolvedOutput) { throw "Output already exists; originals and prior renders are never overwritten: $resolvedOutput" }
$outputParent = Split-Path -Parent $resolvedOutput
if (-not (Test-Path -LiteralPath $outputParent)) { New-Item -ItemType Directory -Path $outputParent -Force | Out-Null }

$ffprobe = Get-Command ffprobe -ErrorAction SilentlyContinue
if ($ffprobe) {
    function Get-MediaDuration([string]$Path) {
        $value = & $ffprobe.Source -v error -show_entries format=duration -of "default=noprint_wrappers=1:nokey=1" $Path 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $value) { throw "FFprobe could not inspect duration: $Path" }
        return [double]::Parse(([string]$value).Trim(), [Globalization.CultureInfo]::InvariantCulture)
    }
    $videoDuration = Get-MediaDuration $ScreenRecording
    $audioDuration = Get-MediaDuration $Voiceover
    $allowedDelta = [Math]::Max(3.0, [Math]::Max($videoDuration, $audioDuration) * 0.05)
    if ([Math]::Abs($videoDuration - $audioDuration) -gt $allowedDelta) {
        throw ("Media duration mismatch is excessive: screen={0:N2}s voice={1:N2}s allowed={2:N2}s." -f $videoDuration, $audioDuration, $allowedDelta)
    }
} else {
    Write-Host "WARN: ffprobe is unavailable; duration mismatch cannot be pre-verified." -ForegroundColor Yellow
}

$arguments = @("-hide_banner", "-n", "-i", $ScreenRecording, "-i", $Voiceover, "-map", "0:v:0", "-map", "1:a:0")
if ($Subtitles) {
    $subtitleFilter = [IO.Path]::GetFullPath($Subtitles).Replace("\", "/").Replace(":", "\:").Replace("'", "\'")
    $arguments += @("-vf", "subtitles=filename='$subtitleFilter'")
}
$arguments += @("-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", $resolvedOutput)
$logRoot = Join-Path $projectRoot ".runtime\recording\media"
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$logPath = Join-Path $logRoot ("render-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
$savedPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    & $ffmpeg.Source @arguments 2>&1 | Tee-Object -FilePath $logPath
    $exitCode = $LASTEXITCODE
} finally { $ErrorActionPreference = $savedPreference }
if ($exitCode -ne 0 -or -not (Test-Path -LiteralPath $resolvedOutput)) { throw "FFmpeg render failed. Log: $logPath" }
Write-Host "Rendered video without modifying originals: $resolvedOutput" -ForegroundColor Green
Write-Host "Log: $logPath"
