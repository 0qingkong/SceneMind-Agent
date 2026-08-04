[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath($PackagePath)
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw "Package directory not found: $root" }
if (-not $OutputPath) { $OutputPath = Join-Path $root "CHECKSUMS.sha256" }
$output = [IO.Path]::GetFullPath($OutputPath)
if (-not $output.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Checksum output must stay inside the package directory."
}

$files = @(Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object { $_.FullName -ne $output } | Sort-Object FullName)
$lines = New-Object System.Collections.Generic.List[string]
foreach ($file in $files) {
    $relative = $file.FullName.Substring($root.Length + 1).Replace("\", "/")
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $lines.Add("$hash  $relative")
}
[IO.File]::WriteAllLines($output, @($lines | ForEach-Object { $_ }), (New-Object Text.UTF8Encoding($false)))
Write-Host "Generated $($files.Count) SHA-256 entries: $output" -ForegroundColor Green
