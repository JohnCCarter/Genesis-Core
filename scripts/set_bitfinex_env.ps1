Write-Warning "[DEPRECATED] scripts/set_bitfinex_env.ps1 moved to scripts/archive/2026-02/analysis/set_bitfinex_env.ps1."
$target = Join-Path $PSScriptRoot 'archive\2026-02\analysis\set_bitfinex_env.ps1'
$resolvedTarget = (Resolve-Path $target).Path
& $resolvedTarget @args
exit $LASTEXITCODE
