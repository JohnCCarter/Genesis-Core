param()
$ErrorActionPreference = "Stop"
python -m black --check src
python -m ruff check src
python -m pytest
python -m bandit -r src
