[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Screenshot,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = "Stop"
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    throw "FFmpeg is unavailable. Deterministic fallback: place the reviewed screenshot on a 1280x720 canvas with 64px horizontal and 36px vertical title-safe margins; export manually and record human approval."
}
if (-not (Test-Path -LiteralPath $Screenshot -PathType Leaf)) { throw "Selected screenshot not found: $Screenshot" }
$source = [IO.Path]::GetFullPath($Screenshot)
$target = [IO.Path]::GetFullPath($Output)
if ($source -eq $target) { throw "Output must differ from the reviewed source screenshot." }
if (Test-Path -LiteralPath $target) { throw "Output already exists and will not be overwritten: $target" }
$parent = Split-Path -Parent $target
if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$filter = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x071512,drawbox=x=64:y=36:w=1152:h=648:color=white@0.22:t=2"
& $ffmpeg.Source -hide_banner -n -i $source -vf $filter -frames:v 1 $target
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $target)) { throw "Thumbnail generation failed." }
Write-Host "Created 1280x720 thumbnail with visible title-safe guide: $target" -ForegroundColor Green
Write-Host "Human title, privacy and final-crop approval remain NOT RUN." -ForegroundColor Yellow
