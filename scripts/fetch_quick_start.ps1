#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick start data fetch for Genesis-Core (matches README.agents.md workflow)

.DESCRIPTION
    Fetches the recommended 18 months of tBTCUSD 1h data (~5 seconds)
#>

Write-Host "========================================" -ForegroundColor Green
Write-Host "Genesis-Core Quick Start Data Fetch" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Fetching: tBTCUSD 1h (18 months)"
Write-Host "Expected time: ~5-10 seconds"
Write-Host "========================================`n" -ForegroundColor Green

python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 1h --months 18

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Success! Now run feature precomputation:" -ForegroundColor Green
    Write-Host "python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
