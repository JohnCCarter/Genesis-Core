<#
Sets Bitfinex credentials as environment variables for the CURRENT PowerShell session.

Why:
- Keep `.env` test-friendly (no real secrets).
- Inject real secrets only when needed.
- Avoid persisting secrets in files that could be read by tools.

Usage:
  .\scripts\set_bitfinex_env.ps1

After running, you can start the API server or run auth-related scripts in the same terminal.

Notes:
- This does NOT write any secrets to disk.
- Environment variables are strings; the secret will exist in process memory while the terminal is open.
#>

$ErrorActionPreference = 'Stop'

function Read-PlainTextFromSecureString {
    param(
        [Parameter(Mandatory = $true)]
        [securestring]$Secure
    )

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

Write-Host "Setting Bitfinex credentials for this session." -ForegroundColor Cyan
Write-Host "Leave blank to keep existing values." -ForegroundColor Cyan

$apiKey = Read-Host "BITFINEX_API_KEY"
$apiSecretSecure = Read-Host "BITFINEX_API_SECRET" -AsSecureString

if ($apiKey -and $apiKey.Trim().Length -gt 0) {
    $Env:BITFINEX_API_KEY = $apiKey.Trim()
}

# Read-Host -AsSecureString always returns a SecureString, even if empty. Convert and check.
$apiSecret = Read-PlainTextFromSecureString -Secure $apiSecretSecure
if ($apiSecret -and $apiSecret.Trim().Length -gt 0) {
    $Env:BITFINEX_API_SECRET = $apiSecret.Trim()
}

Write-Host "Done. Current status:" -ForegroundColor Green
Write-Host ("  BITFINEX_API_KEY set:    {0}" -f [bool]($Env:BITFINEX_API_KEY -and $Env:BITFINEX_API_KEY.Trim()))
Write-Host ("  BITFINEX_API_SECRET set: {0}" -f [bool]($Env:BITFINEX_API_SECRET -and $Env:BITFINEX_API_SECRET.Trim()))

Write-Host ""
Write-Host "Tip: start the API server in this same terminal if you need authenticated endpoints." -ForegroundColor Cyan
