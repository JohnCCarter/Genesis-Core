#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Overnight data fetch - comprehensive dataset for Genesis-Core

.DESCRIPTION
    Fetches 18 months of data for:
    - Primary: tBTCUSD (all timeframes)
    - Secondary: tETHUSD (all timeframes)

    Total time: ~10-15 minutes
#>

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Genesis-Core Overnight Data Collection" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Duration: ~10-15 minutes"
Write-Host "Symbols: tBTCUSD, tETHUSD"
Write-Host "Timeframes: 1m, 5m, 15m, 1h, 6h, 1D"
Write-Host "Period: 18 months"
Write-Host "Note: Using 6h instead of 4h (4h not supported by Bitfinex)"
Write-Host "========================================`n" -ForegroundColor Magenta

$startTime = Get-Date

# Fetch all data using batch script
.\scripts\fetch_all_data.ps1 `
    -Symbols "tBTCUSD,tETHUSD" `
    -Timeframes "1m,5m,15m,1h,6h,1D" `
    -Months 18

$endTime = Get-Date
$duration = ($endTime - $startTime)

Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "OVERNIGHT FETCH COMPLETE" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "Total Duration: $([math]::Round($duration.TotalMinutes, 1)) minutes" -ForegroundColor Green
Write-Host "`nYou can now proceed with feature precomputation!" -ForegroundColor Green
Write-Host "See: README.agents.md for next steps" -ForegroundColor Cyan

exit $LASTEXITCODE
