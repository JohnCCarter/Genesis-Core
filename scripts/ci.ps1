Write-Warning "[DEPRECATED] scripts/ci.ps1 moved to scripts/archive/2026-02/analysis/ci.ps1."
$target = Join-Path $PSScriptRoot 'archive\2026-02\analysis\ci.ps1'
$resolvedTarget = (Resolve-Path $target).Path
& $resolvedTarget @args
exit $LASTEXITCODE
