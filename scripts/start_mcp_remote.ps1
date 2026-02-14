param(
  [int]$Port = 8000,
  [string]$BindHost = "127.0.0.1",
  [string]$SafeRemoteMode = "1",
  [string]$UltraSafeRemoteMode = "0",
  [string]$ConfigPath = "",
  [string]$PythonExe = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
  if (![string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
  }
  $cwd = (Get-Location).Path
  return (Resolve-Path $cwd).Path
}

$repoRoot = Resolve-RepoRoot
Set-Location $repoRoot

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = Join-Path $repoRoot "config\\mcp_settings.remote_safe.json"
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
  $venvPython = Join-Path $repoRoot ".venv\\Scripts\\python.exe"
  if (Test-Path $venvPython) {
    $PythonExe = $venvPython
  } else {
    $PythonExe = "python"
  }
}

$logsDir = Join-Path $repoRoot "logs"
if (!(Test-Path $logsDir)) {
  New-Item -ItemType Directory -Path $logsDir | Out-Null
}
$outLog = Join-Path $logsDir "mcp_remote_stdout.log"
$errLog = Join-Path $logsDir "mcp_remote_stderr.log"

# Remote MCP environment
$env:GENESIS_MCP_PORT = "$Port"
$env:GENESIS_MCP_BIND_HOST = $BindHost
$env:GENESIS_MCP_REMOTE_SAFE = $SafeRemoteMode
$env:GENESIS_MCP_REMOTE_ULTRA_SAFE = $UltraSafeRemoteMode
$env:GENESIS_MCP_CONFIG_PATH = $ConfigPath

Write-Host "Repo: $repoRoot"
Write-Host "Python: $PythonExe"
Write-Host "MCP: http://$BindHost`:$Port  (public via your tunnel hostname)"
Write-Host "Config: $ConfigPath"
Write-Host "Logs: $outLog ; $errLog"

if ($DryRun) {
  exit 0
}

# If something is already listening on the port, avoid starting a second instance.
# - If it looks like MCP (healthz == OK), treat as already-running and exit 0.
# - Otherwise, fail fast with a clear error (avoids silent bind failures on logon).
try {
  $isOpen = $false
  try {
    $isOpen = Test-NetConnection -ComputerName $BindHost -Port $Port -InformationLevel Quiet
  } catch {
    $isOpen = $false
  }

  if ($isOpen) {
    try {
      $health = (Invoke-WebRequest -Uri "http://$BindHost`:$Port/healthz" -UseBasicParsing -TimeoutSec 2).Content
      if (($health + '').Trim() -eq 'OK') {
        Write-Host "MCP already running on port $Port (healthz OK)."
        exit 0
      }
    } catch {}

    Write-Error "Port $Port is already in use and does not appear to be Genesis-Core MCP (/healthz != OK)."
    exit 2
  }
} catch {}

# Keep process in foreground (Scheduled Task stays alive). Redirect output for debugging.
& $PythonExe -m mcp_server.remote_server 1>> $outLog 2>> $errLog
