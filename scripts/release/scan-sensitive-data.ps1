[CmdletBinding()]
param(
    [double]$MaxFileMB = 20,
    [string]$OutputPath = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$tracked = @(& git -C $projectRoot ls-files)
$staged = @(& git -C $projectRoot diff --cached --name-only --diff-filter=ACMR)
$files = @($tracked + $staged | Sort-Object -Unique)
$findings = New-Object System.Collections.Generic.List[object]

function Add-Finding([string]$Severity, [string]$Category, [string]$Path, [int]$Line, [string]$Detail) {
    $findings.Add([pscustomobject]@{ severity = $Severity; category = $Category; path = $Path; line = $Line; detail = $Detail })
}

$forbiddenExtensions = @(".pt", ".onnx", ".db", ".sqlite", ".sqlite3", ".log", ".mp4", ".mov", ".webm")
$textExtensions = @(".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".py", ".ps1", ".ts", ".vue", ".js", ".mjs", ".html", ".css", ".env", ".example", ".srt")
$secretPatterns = @(
    @{ name = "OpenAI-style token"; regex = '(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}' },
    @{ name = "GitHub token"; regex = '(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{20,}' },
    @{ name = "Google API key"; regex = 'AIza[0-9A-Za-z_-]{30,}' },
    @{ name = "AWS access key"; regex = '(?<![A-Z0-9])AKIA[A-Z0-9]{16}(?![A-Z0-9])' },
    @{ name = "Private key material"; regex = '-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----' }
)

foreach ($relative in $files) {
    $normalized = $relative.Replace("\", "/")
    $isScannerSelf = $normalized -eq "scripts/release/scan-sensitive-data.ps1"
    $fullPath = Join-Path $projectRoot $relative
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
    $name = [IO.Path]::GetFileName($relative)
    $extension = [IO.Path]::GetExtension($relative).ToLowerInvariant()

    if ($name -eq ".env" -or $name -match '^(id_rsa|id_ed25519|credentials\.json|secrets?\.json|\.npmrc|\.pypirc)$') {
        Add-Finding "FAIL" "secret filename" $normalized 0 "Sensitive configuration/key filename is tracked."
    }
    if ($normalized -match '(^|/)(\.venv|node_modules|\.runtime|runs)(/|$)' -or
        ($normalized -match '(^|/)frontend/dist(/|$)') -or
        ($normalized -match '(^|/)backend/(data|uploads)/' -and $name -ne ".gitkeep")) {
        Add-Finding "FAIL" "runtime/build artifact" $normalized 0 "Forbidden runtime, dependency or generated path is tracked."
    }
    if ($extension -in $forbiddenExtensions) { Add-Finding "FAIL" "forbidden artifact" $normalized 0 "Model, database, log or recording extension is tracked." }
    if ($extension -match '^\.(png|jpe?g|gif|webp|heic)$' -and $normalized -notmatch '^presentation/screenshots/') {
        Add-Finding "FAIL" "unapproved image" $normalized 0 "Tracked raster image is outside the explicit release-selected screenshot directory."
    }
    $length = (Get-Item -LiteralPath $fullPath).Length
    if ($length -gt $MaxFileMB * 1MB) { Add-Finding "FAIL" "large file" $normalized 0 "File exceeds configured $MaxFileMB MB threshold." }

    if ($extension -in $textExtensions -or $name -in @("Dockerfile", "LICENSE", "VERSION")) {
        try { $lines = [IO.File]::ReadAllLines($fullPath, [Text.Encoding]::UTF8) } catch { continue }
        for ($index = 0; $index -lt $lines.Count; $index++) {
            $line = $lines[$index]
            foreach ($pattern in $secretPatterns) {
                if ($line -match $pattern.regex) { Add-Finding "FAIL" "credential pattern" $normalized ($index + 1) "$($pattern.name) match redacted." }
            }
            if (-not $isScannerSelf -and $line -match '(?i)(?:[A-Z]:\\Users\\[^\\\s]+|/home/[^/\s]+|/Users/[^/\s]+)') {
                Add-Finding "FAIL" "absolute home path" $normalized ($index + 1) "Workstation/user path match redacted."
            }
        }
    }
}

$failed = @($findings | Where-Object { $_.severity -eq "FAIL" })
$payload = [pscustomobject]@{
    ok = $failed.Count -eq 0
    checked_at_utc = [DateTime]::UtcNow.ToString("o")
    tracked_and_staged_files = $files.Count
    max_file_mb = $MaxFileMB
    findings = @($findings | ForEach-Object { $_ })
    limitation = "Pattern and artifact scanning reduces risk but cannot prove that all secrets or private content are absent; human review remains required."
}
if ($OutputPath) {
    $parent = Split-Path -Parent ([IO.Path]::GetFullPath($OutputPath))
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $payload | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}
if ($Json) { $payload | ConvertTo-Json -Depth 7 } else {
    foreach ($finding in $findings) { Write-Host ("[{0}] {1} {2}:{3} - {4}" -f $finding.severity, $finding.category, $finding.path, $finding.line, $finding.detail) }
    Write-Host ("Sensitive-data scan: {0} files; {1} blocking finding(s)." -f $files.Count, $failed.Count)
    Write-Host $payload.limitation -ForegroundColor Yellow
}
if ($failed.Count -gt 0) { exit 1 }
