#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fetch historical data for multiple symbols and timeframes

.DESCRIPTION
    Batch script for overnight data collection. Fetches 18 months of data
    for specified symbols and timeframes with progress tracking.

.PARAMETER Symbols
    Comma-separated list of symbols (default: tBTCUSD,tETHUSD)

.PARAMETER Timeframes
    Comma-separated list of timeframes (default: 1h,4h)

.PARAMETER Months
    Number of months to fetch (default: 18)

.EXAMPLE
    .\fetch_all_data.ps1
    .\fetch_all_data.ps1 -Symbols "tBTCUSD,tETHUSD" -Timeframes "1m,5m,15m,1h,4h,1D" -Months 18
#>

param(
    [string]$Symbols = "tBTCUSD,tETHUSD",
    [string]$Timeframes = "1h,4h",
    [int]$Months = 18
)

$ErrorActionPreference = "Continue"  # Continue on errors

# Parse comma-separated lists
$symbolList = $Symbols -split ',' | ForEach-Object { $_.Trim() }
$timeframeList = $Timeframes -split ',' | ForEach-Object { $_.Trim() }

# Calculate total jobs
$totalJobs = $symbolList.Count * $timeframeList.Count
$currentJob = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Genesis-Core Batch Data Fetcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Symbols:    $Symbols"
Write-Host "Timeframes: $Timeframes"
Write-Host "Months:     $Months"
Write-Host "Total Jobs: $totalJobs"
Write-Host "========================================`n" -ForegroundColor Cyan

$startTime = Get-Date
$results = @()

foreach ($symbol in $symbolList) {
    foreach ($timeframe in $timeframeList) {
        $currentJob++

        Write-Host "[$currentJob/$totalJobs] Fetching $symbol $timeframe..." -ForegroundColor Yellow

        $jobStart = Get-Date

        try {
            # Run fetch script
            python scripts/fetch_historical.py `
                --symbol $symbol `
                --timeframe $timeframe `
                --months $Months

            $jobEnd = Get-Date
            $duration = ($jobEnd - $jobStart).TotalSeconds

            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Success ($([math]::Round($duration, 1))s)`n" -ForegroundColor Green
                $results += [PSCustomObject]@{
                    Symbol = $symbol
                    Timeframe = $timeframe
                    Status = "✅ Success"
                    Duration = "$([math]::Round($duration, 1))s"
                }
            } else {
                Write-Host "  ❌ Failed (exit code: $LASTEXITCODE)`n" -ForegroundColor Red
                $results += [PSCustomObject]@{
                    Symbol = $symbol
                    Timeframe = $timeframe
                    Status = "❌ Failed"
                    Duration = "$([math]::Round($duration, 1))s"
                }
            }
        }
        catch {
            Write-Host "  ❌ Error: $($_.Exception.Message)`n" -ForegroundColor Red
            $results += [PSCustomObject]@{
                Symbol = $symbol
                Timeframe = $timeframe
                Status = "❌ Error"
                Duration = "N/A"
            }
        }
    }
}

$endTime = Get-Date
$totalDuration = ($endTime - $startTime)

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BATCH FETCH SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$results | Format-Table -AutoSize

Write-Host "Total Duration: $([math]::Round($totalDuration.TotalMinutes, 1)) minutes" -ForegroundColor Cyan
Write-Host "Successful: $($results | Where-Object { $_.Status -eq '✅ Success' } | Measure-Object | Select-Object -ExpandProperty Count)/$totalJobs" -ForegroundColor Green
Write-Host "Failed: $($results | Where-Object { $_.Status -ne '✅ Success' } | Measure-Object | Select-Object -ExpandProperty Count)/$totalJobs" -ForegroundColor Red

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Validate data integrity:"
Write-Host "   python scripts/validate_data.py --symbol tBTCUSD --timeframe 1h"
Write-Host ""
Write-Host "2. Precompute features (vectorized - FAST!):"
Write-Host "   python scripts/precompute_features_v17.py --symbol tBTCUSD --timeframe 1h"
Write-Host ""
Write-Host "3. Train model:"
Write-Host "   python scripts/train_model.py --symbol tBTCUSD --timeframe 1h --use-holdout"
Write-Host ""

# Exit with error code if any job failed
if ($results | Where-Object { $_.Status -ne '✅ Success' }) {
    exit 1
} else {
    exit 0
}
