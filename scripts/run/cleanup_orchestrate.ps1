#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [ValidateSet("hard", "shard-a", "shard-b", "shard-c", "all")]
    [string]$Mode = "hard",

    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,

    [string]$PythonExe,
    [string]$SemgrepExe,
    [string]$JscpdExe,

    [string]$ReportRoot,

    [switch]$DryRun,
    [switch]$FailOnFindings
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

if (-not $PythonExe) {
    $PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
}
if (-not $SemgrepExe) {
    $SemgrepExe = Join-Path $env:LOCALAPPDATA "DevTools\pytools\Scripts\semgrep.exe"
}
if (-not $JscpdExe) {
    $JscpdExe = Join-Path $env:LOCALAPPDATA "Programs\nodejs\jscpd.cmd"
}
if (-not $ReportRoot) {
    $ReportRoot = Join-Path $RepoRoot "reports\cleanup-orchestration"
}

foreach ($tool in @($PythonExe, $SemgrepExe, $JscpdExe)) {
    if (-not (Test-Path $tool)) {
        throw "Required tool not found: $tool"
    }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir = Join-Path $ReportRoot ("{0}_{1}" -f $Mode, $timestamp)
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $runDir "logs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $runDir "jscpd") -Force | Out-Null

$results = New-Object System.Collections.Generic.List[object]
$script:stepCounter = 0

function Invoke-OrchestratedStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Phase,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Executable,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [int[]]$AllowedExitCodes = @(0)
    )

    $script:stepCounter += 1
    $safeName = ($Name -replace "[^a-zA-Z0-9_-]", "_")
    $logFile = Join-Path $runDir ("logs\{0:d2}_{1}_{2}.log" -f $script:stepCounter, $Phase, $safeName)

    Write-Host "[${Phase}] ${Name}" -ForegroundColor Cyan
    Write-Host "  $Executable $($Arguments -join ' ')"

    if ($DryRun) {
        $result = [PSCustomObject]@{
            phase = $Phase
            step = $Name
            executable = $Executable
            args = $Arguments
            exit_code = 0
            status = "DRYRUN"
            log = $logFile
        }
        $results.Add($result)
        return $result
    }

    Push-Location $RepoRoot
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Executable @Arguments *>&1 | Tee-Object -FilePath $logFile | Out-Host
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
        Pop-Location
    }

    $status = if ($AllowedExitCodes -contains $exitCode) {
        if ($exitCode -eq 0) { "PASS" } else { "WARN" }
    }
    else {
        "FAIL"
    }

    if ($status -eq "FAIL") {
        Write-Host "  -> FAIL (exit=$exitCode)" -ForegroundColor Red
    }
    elseif ($status -eq "WARN") {
        Write-Host "  -> WARN (exit=$exitCode, findings detected)" -ForegroundColor Yellow
    }
    else {
        Write-Host "  -> PASS" -ForegroundColor Green
    }

    $result = [PSCustomObject]@{
        phase = $Phase
        step = $Name
        executable = $Executable
        args = $Arguments
        exit_code = $exitCode
        status = $status
        log = $logFile
    }
    $results.Add($result)
    return $result
}

function Invoke-HardProfile {
    param([string]$PhaseName = "hard")

    $radonExclude = ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive"

    Invoke-OrchestratedStep -Phase $PhaseName -Name "semgrep" -Executable $SemgrepExe -Arguments @(
        "scan", "--config", "p/python", "--metrics", "off", "--quiet",
        "--exclude", "scripts/archive", "."
    ) | Out-Null

    Invoke-OrchestratedStep -Phase $PhaseName -Name "jscpd" -Executable $JscpdExe -Arguments @(
        "--config", ".jscpd.json", "--mode", "weak", "--silent", "--exitCode", "0",
        "--output", (Join-Path $runDir "jscpd\$PhaseName"), "."
    ) -AllowedExitCodes @(0, 1) | Out-Null

    Invoke-OrchestratedStep -Phase $PhaseName -Name "vulture" -Executable $PythonExe -Arguments @(
        "-m", "vulture", "--config", "pyproject.toml", "src/core", "mcp_server", "scripts", "tests"
    ) -AllowedExitCodes @(0, 3) | Out-Null

    Invoke-OrchestratedStep -Phase $PhaseName -Name "radon_cc" -Executable $PythonExe -Arguments @(
        "-m", "radon", "cc", "src", "mcp_server", "scripts", "tests",
        "--exclude", $radonExclude, "--ignore", "__pycache__"
    ) | Out-Null
}

function Invoke-ShardAProfile {
    $radonExclude = ".venv,artifacts,cache,data,logs,results,tmp,reports"

    Invoke-OrchestratedStep -Phase "shard-a" -Name "semgrep" -Executable $SemgrepExe -Arguments @(
        "scan", "--config", "p/python", "--metrics", "off", "--quiet",
        "scripts", "scripts/archive",
        "--exclude", ".venv", "--exclude", "artifacts", "--exclude", "cache",
        "--exclude", "data", "--exclude", "logs", "--exclude", "results",
        "--exclude", "tmp", "--exclude", "reports"
    ) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-a" -Name "jscpd" -Executable $JscpdExe -Arguments @(
        "--config", ".jscpd.shard-a.json", "--mode", "weak", "--silent", "--exitCode", "0",
        "--output", (Join-Path $runDir "jscpd\shard-a"), "scripts"
    ) -AllowedExitCodes @(0, 1) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-a" -Name "vulture" -Executable $PythonExe -Arguments @(
        "-m", "vulture", "--config", "tools/config/vulture_shard_a.toml", "scripts", "scripts/archive"
    ) -AllowedExitCodes @(0, 3) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-a" -Name "radon_cc" -Executable $PythonExe -Arguments @(
        "-m", "radon", "cc", "scripts", "scripts/archive",
        "--exclude", $radonExclude, "--ignore", "__pycache__"
    ) | Out-Null
}

function Invoke-ShardBProfile {
    $radonExclude = ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive"

    Invoke-OrchestratedStep -Phase "shard-b" -Name "semgrep" -Executable $SemgrepExe -Arguments @(
        "scan", "--config", "p/python", "--metrics", "off", "--quiet", "tests"
    ) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-b" -Name "jscpd" -Executable $JscpdExe -Arguments @(
        "--config", ".jscpd.json", "--mode", "weak", "--silent", "--exitCode", "0",
        "--output", (Join-Path $runDir "jscpd\shard-b"), "tests"
    ) -AllowedExitCodes @(0, 1) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-b" -Name "vulture" -Executable $PythonExe -Arguments @(
        "-m", "vulture", "--config", "pyproject.toml", "tests"
    ) -AllowedExitCodes @(0, 3) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-b" -Name "radon_cc" -Executable $PythonExe -Arguments @(
        "-m", "radon", "cc", "tests",
        "--exclude", $radonExclude, "--ignore", "__pycache__"
    ) | Out-Null
}

function Invoke-ShardCProfile {
    $radonExclude = ".venv,archive,artifacts,cache,data,logs,results,tmp,reports,scripts/archive"

    Invoke-OrchestratedStep -Phase "shard-c" -Name "semgrep" -Executable $SemgrepExe -Arguments @(
        "scan", "--config", "p/python", "--metrics", "off", "--quiet", "src/core", "mcp_server"
    ) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-c" -Name "jscpd" -Executable $JscpdExe -Arguments @(
        "--config", ".jscpd.json", "--mode", "weak", "--silent", "--exitCode", "0",
        "--output", (Join-Path $runDir "jscpd\shard-c"), "src/core", "mcp_server"
    ) -AllowedExitCodes @(0, 1) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-c" -Name "vulture" -Executable $PythonExe -Arguments @(
        "-m", "vulture", "--config", "pyproject.toml", "src/core", "mcp_server"
    ) -AllowedExitCodes @(0, 3) | Out-Null

    Invoke-OrchestratedStep -Phase "shard-c" -Name "radon_cc" -Executable $PythonExe -Arguments @(
        "-m", "radon", "cc", "src/core", "mcp_server",
        "--exclude", $radonExclude, "--ignore", "__pycache__"
    ) | Out-Null
}

Write-Host "Cleanup orchestration mode: $Mode" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"
Write-Host "Report dir: $runDir"
Write-Host ""

switch ($Mode) {
    "hard" { Invoke-HardProfile }
    "shard-a" { Invoke-ShardAProfile }
    "shard-b" { Invoke-ShardBProfile }
    "shard-c" { Invoke-ShardCProfile }
    "all" {
        Invoke-HardProfile -PhaseName "hard"
        Invoke-ShardAProfile
        Invoke-ShardBProfile
        Invoke-ShardCProfile
    }
}

$summaryJson = Join-Path $runDir "summary.json"
$summaryMd = Join-Path $runDir "summary.md"

$results | ConvertTo-Json -Depth 5 | Set-Content -Path $summaryJson -Encoding UTF8

$md = @()
$md += "# Cleanup Orchestration Summary"
$md += ""
$md += "- mode: $Mode"
$md += "- repo: $RepoRoot"
$md += "- generated: $(Get-Date -Format o)"
$md += ""
$md += "| phase | step | status | exit | log |"
$md += "|---|---|---:|---:|---|"
foreach ($r in $results) {
    $md += "| $($r.phase) | $($r.step) | $($r.status) | $($r.exit_code) | $($r.log) |"
}
$md -join "`n" | Set-Content -Path $summaryMd -Encoding UTF8

$failCount = @($results | Where-Object { $_.status -eq "FAIL" }).Count
$warnCount = @($results | Where-Object { $_.status -eq "WARN" }).Count
$passCount = @($results | Where-Object { $_.status -eq "PASS" }).Count
$dryCount = @($results | Where-Object { $_.status -eq "DRYRUN" }).Count

Write-Host ""
Write-Host "Summary: pass=$passCount warn=$warnCount fail=$failCount dryrun=$dryCount" -ForegroundColor Cyan
Write-Host "Artifacts:"
Write-Host "  $summaryJson"
Write-Host "  $summaryMd"

if ($failCount -gt 0) {
    exit 1
}
if ($FailOnFindings -and $warnCount -gt 0) {
    exit 2
}
exit 0
