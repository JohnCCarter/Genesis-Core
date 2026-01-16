param()
$ErrorActionPreference = "Stop"

Write-Host "Running CI checks..." -ForegroundColor Green

Write-Host "1. Lint/format/secrets (pre-commit)..." -ForegroundColor Yellow
python -m pre_commit run --all-files
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "2. Security scan (bandit)..." -ForegroundColor Yellow
python -m bandit -r src -c bandit.yaml
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "3. Running tests (pytest)..." -ForegroundColor Yellow
python -m pytest --tb=short -q
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "All CI checks passed!" -ForegroundColor Green
