[CmdletBinding()]
param(
    [string]$ApiBase = "http://127.0.0.1:8000/api/v1",
    [switch]$Extended
)

$ErrorActionPreference = "Stop"

function Invoke-SmokeRequest {
    param(
        [string]$Name,
        [string]$Uri,
        [string]$Method = "GET",
        [string]$Body = "",
        [int[]]$Expected = @(200)
    )
    try {
        $parameters = @{ Uri = $Uri; Method = $Method; UseBasicParsing = $true; TimeoutSec = 10; ErrorAction = "Stop" }
        if ($Body) {
            $parameters["Body"] = [System.Text.Encoding]::UTF8.GetBytes($Body)
            $parameters["ContentType"] = "application/json; charset=utf-8"
        }
        $response = Invoke-WebRequest @parameters
        $status = [int]$response.StatusCode
        $content = $response.Content
    } catch {
        $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
        $content = ""
    }
    if ($status -notin $Expected) { throw "$Name failed with HTTP $status at $Uri" }
    Write-Host ("PASS {0,-18} HTTP {1}" -f $Name, $status) -ForegroundColor Green
    if ($content) { return ($content | ConvertFrom-Json) }
    return $null
}

Invoke-SmokeRequest "health" "$ApiBase/health" | Out-Null
$ready = Invoke-SmokeRequest "readiness" "$ApiBase/ready"
if ($ready.status -ne "ready") { throw "Readiness payload was not ready." }
Invoke-SmokeRequest "observations" "$ApiBase/observations?limit=5" | Out-Null
Invoke-SmokeRequest "last-seen" "$ApiBase/memory/last-seen?q=cup" -Expected @(200, 404) | Out-Null
Invoke-SmokeRequest "history" "$ApiBase/memory/history?q=cup" | Out-Null
Invoke-SmokeRequest "Agent query" "$ApiBase/agent/query" -Method POST -Body '{"query":"Where was my cup last seen?"}' | Out-Null
Invoke-SmokeRequest "capture sessions" "$ApiBase/capture-sessions" | Out-Null
Invoke-SmokeRequest "device stats" "$ApiBase/devices/stats" | Out-Null
Invoke-SmokeRequest "insights" "$ApiBase/insights" | Out-Null

if ($Extended) {
    $created = Invoke-SmokeRequest "create session" "$ApiBase/capture-sessions" -Method POST -Body '{"title":"Smoke verification","source_type":"browser_camera","sample_interval_seconds":5,"auto_save_mode":"manual"}' -Expected @(201)
    $id = [string]$created.id
    Invoke-SmokeRequest "stop session" "$ApiBase/capture-sessions/$id/stop" -Method POST | Out-Null
    Invoke-SmokeRequest "delete session" "$ApiBase/capture-sessions/$id" -Method DELETE -Expected @(204) | Out-Null
}
Write-Host "SceneMind smoke verification passed." -ForegroundColor Green
