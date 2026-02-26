Write-Warning "[DEPRECATED] scripts/fetch_overnight.ps1 moved to scripts/archive/2026-02/analysis/fetch_overnight.ps1."
$target = Join-Path $PSScriptRoot 'archive\2026-02\analysis\fetch_overnight.ps1'
$resolvedTarget = (Resolve-Path $target).Path
& $resolvedTarget @args
exit $LASTEXITCODE
