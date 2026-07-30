Set-StrictMode -Version 2.0

$script:SceneMindProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))

function Get-SceneMindProjectRoot {
    return $script:SceneMindProjectRoot
}

function Get-SceneMindRuntimeRoot {
    return (Join-Path $script:SceneMindProjectRoot ".runtime")
}

function Initialize-SceneMindRuntime {
    $runtimeRoot = Get-SceneMindRuntimeRoot
    foreach ($name in @("pids", "logs", "status")) {
        $path = Join-Path $runtimeRoot $name
        if (-not (Test-Path -LiteralPath $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
    return $runtimeRoot
}

function Import-SceneMindEnv {
    param([string]$Path = (Join-Path $script:SceneMindProjectRoot ".env"))

    if (-not (Test-Path -LiteralPath $Path)) { return }
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
        $parts = $trimmed.Split(@("="), 2, [System.StringSplitOptions]::None)
        $name = $parts[0].Trim()
        if ($name -notmatch "^[A-Za-z_][A-Za-z0-9_]*$") { continue }
        if (-not [Environment]::GetEnvironmentVariable($name, "Process")) {
            [Environment]::SetEnvironmentVariable($name, $parts[1].Trim(), "Process")
        }
    }
}

function Test-SceneMindPortAvailable {
    param(
        [Parameter(Mandatory = $true)][int]$Port,
        [string]$HostAddress = "127.0.0.1"
    )

    $address = if ($HostAddress -eq "0.0.0.0") {
        [System.Net.IPAddress]::Any
    } else {
        [System.Net.IPAddress]::Parse($HostAddress)
    }
    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener($address, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($null -ne $listener) { $listener.Stop() }
    }
}

function Wait-SceneMindHttp {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [int]$TimeoutSeconds = 45,
        [scriptblock]$Validator
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $response = Invoke-RestMethod -Uri $Uri -Method Get -TimeoutSec 4 -ErrorAction Stop
            if ($null -eq $Validator -or (& $Validator $response)) { return $true }
        } catch {
            Start-Sleep -Milliseconds 500
            continue
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Get-SceneMindPidPath {
    param([Parameter(Mandatory = $true)][string]$Role)
    return (Join-Path (Join-Path (Get-SceneMindRuntimeRoot) "pids") "$Role.json")
}

function Save-SceneMindProcessMetadata {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$Role,
        [Parameter(Mandatory = $true)][string]$Command,
        [hashtable]$Extra = @{}
    )

    Initialize-SceneMindRuntime | Out-Null
    $metadata = [ordered]@{
        role = $Role
        pid = $Process.Id
        process_name = $Process.ProcessName
        start_time_utc = $Process.StartTime.ToUniversalTime().ToString("o")
        command = $Command
        project_root = $script:SceneMindProjectRoot
    }
    foreach ($key in $Extra.Keys) { $metadata[$key] = $Extra[$key] }
    $metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Get-SceneMindPidPath $Role) -Encoding UTF8
    return [pscustomobject]$metadata
}

function Read-SceneMindProcessMetadata {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

function Test-SceneMindProcessIdentity {
    param([Parameter(Mandatory = $true)]$Metadata)

    if ($null -eq $Metadata -or $null -eq $Metadata.pid) { return $false }
    $process = Get-Process -Id ([int]$Metadata.pid) -ErrorAction SilentlyContinue
    if ($null -eq $process) { return $false }
    try {
        $expected = [DateTime]::Parse([string]$Metadata.start_time_utc).ToUniversalTime()
        $actual = $process.StartTime.ToUniversalTime()
        $sameStart = [Math]::Abs(($actual - $expected).TotalSeconds) -lt 3
        return $sameStart -and $process.ProcessName -eq [string]$Metadata.process_name
    } catch {
        return $false
    }
}

function Get-SceneMindDescendantPids {
    param([Parameter(Mandatory = $true)][int]$ParentPid)

    $result = New-Object System.Collections.Generic.List[int]
    $queue = New-Object System.Collections.Generic.Queue[int]
    $queue.Enqueue($ParentPid)
    try { $all = @(Get-CimInstance Win32_Process -ErrorAction Stop) } catch { return @() }
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        foreach ($child in $all | Where-Object { [int]$_.ParentProcessId -eq $current }) {
            $childPid = [int]$child.ProcessId
            if (-not $result.Contains($childPid)) {
                $result.Add($childPid)
                $queue.Enqueue($childPid)
            }
        }
    }
    return @($result)
}

function Stop-SceneMindManagedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$MetadataPath,
        [switch]$Force
    )

    $metadata = Read-SceneMindProcessMetadata $MetadataPath
    if ($null -eq $metadata) {
        if (Test-Path -LiteralPath $MetadataPath) { Remove-Item -LiteralPath $MetadataPath -Force }
        return $false
    }
    if (-not (Test-SceneMindProcessIdentity $metadata)) {
        Remove-Item -LiteralPath $MetadataPath -Force -ErrorAction SilentlyContinue
        return $false
    }

    $rootPid = [int]$metadata.pid

    # Start-Process may return an npm/cmd wrapper whose children keep Vite's
    # native modules open after the wrapper exits. taskkill /T is scoped to the
    # already identity-verified PID and remains reliable when CIM inspection is
    # unavailable to a non-administrator shell.
    if ($env:OS -eq "Windows_NT") {
        $arguments = @("/PID", [string]$rootPid, "/T")
        if ($Force) { $arguments += "/F" }
        & taskkill.exe @arguments 2>$null | Out-Null
        if ((Get-Process -Id $rootPid -ErrorAction SilentlyContinue) -and -not $Force) {
            & taskkill.exe /PID $rootPid /T /F 2>$null | Out-Null
        }
    } else {
        $descendants = @(Get-SceneMindDescendantPids $rootPid)
        $targets = @($descendants | Sort-Object -Descending) + @($rootPid)
        foreach ($targetPid in $targets) {
            Stop-Process -Id $targetPid -Force -ErrorAction SilentlyContinue
        }
    }
    Remove-Item -LiteralPath $MetadataPath -Force -ErrorAction SilentlyContinue
    return $true
}

function Get-SceneMindLogTail {
    param([Parameter(Mandatory = $true)][string]$Path, [int]$Lines = 25)
    if (-not (Test-Path -LiteralPath $Path)) { return "(log file not created)" }
    return ((Get-Content -LiteralPath $Path -Tail $Lines -ErrorAction SilentlyContinue) -join [Environment]::NewLine)
}
