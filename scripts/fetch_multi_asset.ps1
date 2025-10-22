#!/usr/bin/env pwsh
# Quick fetch för multi-asset testing
Write-Host "Fetching top 3 crypto (BTC, ETH, SOL) on 1h..." -ForegroundColor Cyan

.\scripts\fetch_all_data.ps1 `
    -Symbols "tBTCUSD,tETHUSD,tSOLUSD" `
    -Timeframes "1h" `
    -Months 18

Write-Host "`nNext: Train models for each asset!" -ForegroundColor Green
Write-Host "python scripts/train_model.py --symbol tETHUSD --timeframe 1h --use-holdout" -ForegroundColor Yellow
