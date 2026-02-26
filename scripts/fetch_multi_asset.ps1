Write-Warning "[DEPRECATED] scripts/fetch_multi_asset.ps1 moved to scripts/archive/2026-02/analysis/fetch_multi_asset.ps1."
$target = Join-Path $PSScriptRoot 'archive\2026-02\analysis\fetch_multi_asset.ps1'
$resolvedTarget = (Resolve-Path $target).Path
& $resolvedTarget @args
exit $LASTEXITCODE
