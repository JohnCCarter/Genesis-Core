param()
$ErrorActionPreference = "Stop"

Write-Host "Running CI checks..." -ForegroundColor Green

Write-Host "1. Code formatting (black)..." -ForegroundColor Yellow
python -m black --check src scripts tests
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "2. Linting (ruff)..." -ForegroundColor Yellow
python -m ruff check src scripts tests
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "3. Security scan (bandit)..." -ForegroundColor Yellow
python -m bandit -r src
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "4. Running tests (pytest)..." -ForegroundColor Yellow
python -m pytest --tb=short -q
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "All CI checks passed!" -ForegroundColor Green
