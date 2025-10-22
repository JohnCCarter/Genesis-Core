#!/usr/bin/env pwsh
# Quick fetch för trend-following hypotes test (TODO.md Option A)
# Note: Using 3h and 6h instead of 4h (4h not supported by Bitfinex API)
Write-Host "Fetching 3h, 6h + 1D for trend-following test..." -ForegroundColor Cyan
Write-Host "Note: 4h is NOT supported by Bitfinex. Using 3h and 6h instead." -ForegroundColor Yellow

.\scripts\fetch_all_data.ps1 `
    -Symbols "tBTCUSD" `
    -Timeframes "3h,6h,1D" `
    -Months 12

Write-Host "`nNext: Run feature analysis to check if trend features have positive IC!" -ForegroundColor Green
Write-Host "python scripts/comprehensive_feature_analysis.py --symbol tBTCUSD --timeframe 6h" -ForegroundColor Yellow
