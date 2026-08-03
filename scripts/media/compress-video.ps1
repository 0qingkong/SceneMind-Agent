[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Input,
    [Parameter(Mandatory = $true)][string]$Output,
    [ValidateSet("high-quality", "competition-upload", "small-backup")][string]$Preset = "competition-upload"
)

$ErrorActionPreference = "Stop"
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) { throw "FFmpeg is not available. This script does not download external tools." }
if (-not (Test-Path -LiteralPath $Input -PathType Leaf)) { throw "Input video not found: $Input" }
$source = [IO.Path]::GetFullPath($Input)
$target = [IO.Path]::GetFullPath($Output)
if ($source -eq $target) { throw "Output must differ from source." }
if (Test-Path -LiteralPath $target) { throw "Output already exists and will not be overwritten: $target" }
$parent = Split-Path -Parent $target
if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }

$settings = @{
    "high-quality" = @{ crf = "18"; scale = "-2:1080"; audio = "192k"; preset = "slow" }
    "competition-upload" = @{ crf = "22"; scale = "-2:1080"; audio = "160k"; preset = "medium" }
    "small-backup" = @{ crf = "28"; scale = "-2:720"; audio = "96k"; preset = "fast" }
}[$Preset]
$arguments = @(
    "-hide_banner", "-n", "-i", $source, "-vf", "scale=$($settings.scale):force_original_aspect_ratio=decrease",
    "-c:v", "libx264", "-preset", $settings.preset, "-crf", $settings.crf, "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", $settings.audio, "-movflags", "+faststart", $target
)
& $ffmpeg.Source @arguments
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $target)) { throw "FFmpeg compression failed." }
Write-Host "Created $Preset copy: $target" -ForegroundColor Green
Write-Host "Original preserved: $source"
