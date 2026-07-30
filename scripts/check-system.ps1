[CmdletBinding()]
param([switch]$Json)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "lib\common.ps1")

$projectRoot = Get-SceneMindProjectRoot
$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$Name, [string]$Status, [string]$Detail) {
    $checks.Add([pscustomobject]@{ name = $Name; status = $Status; detail = $Detail })
}

$git = Get-Command git -ErrorAction SilentlyContinue
Add-Check "Git" $(if ($git) { "PASS" } else { "FAIL" }) $(if ($git) { (& $git.Source --version) } else { "Install Git." })

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $pythonExe) { $pythonExe } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
if ($python) {
    $pythonVersion = (& $python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null)
    $pythonMajorMinor = [version]$pythonVersion
    Add-Check "Python" $(if ($pythonMajorMinor -ge [version]"3.11") { "PASS" } else { "FAIL" }) $pythonVersion
} else { Add-Check "Python" "FAIL" "Install Python 3.11 or later." }

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) { Add-Check "Node.js" "PASS" ((& $node.Source --version) -join "") } else { Add-Check "Node.js" "FAIL" "Install Node.js 20.19+ or 22.12+." }
$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) { $npm = Get-Command npm -ErrorAction SilentlyContinue }
if ($npm) { Add-Check "npm" "PASS" ((& $npm.Source --version) -join "") } else { Add-Check "npm" "FAIL" "npm was not found." }

$required = @("backend\requirements.txt", "backend\app\main.py", "frontend\package.json", "frontend\package-lock.json")
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $projectRoot $_)) })
Add-Check "Repository" $(if ($missing.Count -eq 0) { "PASS" } else { "FAIL" }) $(if ($missing.Count -eq 0) { "Required manifests found." } else { "Missing: $($missing -join ', ')" })

$runtimeRoot = Get-SceneMindRuntimeRoot
if ($Json) {
    $runtimeParent = Split-Path -Parent $runtimeRoot
    Add-Check "Runtime directory" $(if (Test-Path -LiteralPath $runtimeParent) { "PASS" } else { "FAIL" }) "JSON mode performed a read-only parent check."
} else {
    try {
        Initialize-SceneMindRuntime | Out-Null
        $probe = Join-Path (Join-Path $runtimeRoot "status") ("write-probe-{0}.tmp" -f [Guid]::NewGuid())
        [System.IO.File]::WriteAllText($probe, "ok")
        Remove-Item -LiteralPath $probe -Force
        Add-Check "Runtime directory" "PASS" "Writable."
    } catch { Add-Check "Runtime directory" "FAIL" "Not writable: $($_.Exception.Message)" }
}

foreach ($port in @(8000, 5173)) {
    $available = Test-SceneMindPortAvailable -Port $port
    Add-Check "Port $port" $(if ($available) { "PASS" } else { "FAIL" }) $(if ($available) { "Available." } else { "Occupied; stop the owning service or choose another port." })
}

$driveRoot = [System.IO.Path]::GetPathRoot($projectRoot)
try {
    $drive = New-Object System.IO.DriveInfo($driveRoot)
    $freeGb = [Math]::Round($drive.AvailableFreeSpace / 1GB, 2)
    $diskStatus = if ($freeGb -ge 2) { "PASS" } elseif ($freeGb -ge 0.5) { "WARN" } else { "FAIL" }
    Add-Check "Disk space" $diskStatus "$freeGb GB free."
} catch { Add-Check "Disk space" "WARN" "Unable to inspect free space." }

$psVersion = $PSVersionTable.PSVersion.ToString()
Add-Check "PowerShell" $(if ($PSVersionTable.PSVersion -ge [version]"5.1") { "PASS" } else { "FAIL" }) $psVersion

if (Test-Path -LiteralPath $pythonExe) {
    try {
        $torchJson = & $pythonExe -c "import json; import torch; print(json.dumps({'torch': torch.__version__, 'cuda': bool(torch.cuda.is_available()), 'device_count': int(torch.cuda.device_count())}))" 2>$null
        $torch = $torchJson | ConvertFrom-Json
        Add-Check "PyTorch/CUDA" "PASS" "torch $($torch.torch); CUDA=$($torch.cuda); devices=$($torch.device_count)"
    } catch { Add-Check "PyTorch/CUDA" "WARN" "PyTorch unavailable or failed to load." }
} else { Add-Check "PyTorch/CUDA" "WARN" "Run setup to create .venv." }

Import-SceneMindEnv
$modelName = if ($env:YOLO_MODEL) { $env:YOLO_MODEL } else { "yolo26n.pt" }
$modelCandidates = @((Join-Path $projectRoot $modelName), (Join-Path (Join-Path $projectRoot "backend") $modelName))
$modelPresent = @($modelCandidates | Where-Object { Test-Path -LiteralPath $_ }).Count -gt 0
Add-Check "YOLO weights" $(if ($modelPresent) { "PASS" } else { "WARN" }) $(if ($modelPresent) { "Configured model file is present." } else { "Not found locally; setup never downloads it unless -DownloadModel is supplied." })

$hasFailure = @($checks | Where-Object { $_.status -eq "FAIL" }).Count -gt 0
if ($Json) {
    $checkItems = @($checks | ForEach-Object { $_ })
    [pscustomobject]@{ ok = -not $hasFailure; checks = $checkItems } | ConvertTo-Json -Depth 5
} else {
    foreach ($item in $checks) {
        $color = if ($item.status -eq "PASS") { "Green" } elseif ($item.status -eq "WARN") { "Yellow" } else { "Red" }
        Write-Host ("{0,-5} {1,-20} {2}" -f $item.status, $item.name, $item.detail) -ForegroundColor $color
    }
}
if ($hasFailure) { exit 1 }
