# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Genesis-Core is a Python 3.11+ trading system with deterministic backtesting/optimization and a FastAPI service for trading strategy execution. The system focuses on reproducibility, paper trading safety, and configuration-driven runtime behavior.

**Core Principles:**

- **Reproducibility**: Same config + same data = same results (canonical mode: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`)
- **Paper Trading Safety**: Paper orders restricted to whitelisted TEST symbols
- **SSOT Config**: Runtime config managed via `config/runtime.json` and config API

## Development Setup

```powershell
# Windows PowerShell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

# Start API locally
uvicorn core.server:app --reload --app-dir src

# Verify tooling
pre-commit run --all-files
python -m pytest
```

## Common Commands

### Running Tests

```powershell
# Full test suite
python -m pytest

# Specific test file
python -m pytest tests/test_backtest_engine.py -v

# Run with coverage
python -m pytest --cov=src/core
```

### Code Quality

```powershell
# Format code
black src/ tests/ scripts/

# Lint
ruff check src/ tests/

# Security scan (first-party code only)
bandit -r src -ll --skip B101,B102,B110

# Pre-commit hooks
pre-commit run --all-files
```

### Backtesting

```powershell
# Run backtest with canonical mode
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-01-01 --end 2024-12-31
```

### Optimization (Optuna)

```powershell
# Always validate before long runs
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml

# Set canonical environment
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_MAX_CONCURRENT='4'
$Env:GENESIS_RANDOM_SEED='42'

# Run optimizer
python -c "from core.optimizer.runner import run_optimizer; from pathlib import Path; run_optimizer(Path('config/optimizer/<config>.yaml'))"

# Summarize results
python scripts/optimizer.py summarize run_<YYYYMMDD_HHMMSS> --top 10
```

## Architecture

### Directory Structure

```
src/core/              # Main application code
├── backtest/          # Backtest engine and metrics
├── config/            # Configuration validation
├── indicators/        # Technical indicators (EMA, RSI, ADX, ATR, Fibonacci)
├── io/bitfinex/       # Exchange integration
├── ml/                # Machine learning components
├── observability/     # Metrics and monitoring
├── optimizer/         # Optuna integration
├── risk/              # Risk management
├── strategy/          # Trading strategy (features, decision, evaluate)
├── symbols/           # Symbol mapping (realistic/synthetic modes)
└── utils/             # Utilities (nonce, logging, backoff)

config/                # Configuration files
├── models/            # Model configs (separate from registry governance)
├── optimizer/         # Optuna configs
├── runtime.json       # SSOT runtime config (gitignored)
└── strategy/champions/  # Champion strategy configs

scripts/               # Utility scripts
├── run_backtest.py    # Manual backtest runner
├── preflight_optuna_check.py  # Pre-optimization validation
├── validate_optimizer_config.py  # Config validation
└── optimizer.py       # Result analysis

tests/                 # Test files (pytest)
data/                  # Market data (raw/curated)
results/               # Backtest results and optimizer artifacts
registry/              # Governance (skills/compacts/manifests/schemas)
```

### Strategy Pipeline

1. **Feature Extraction**: EMA delta %, RSI, ADX, ATR, Fibonacci levels
2. **Probability Model**: ML-based probability prediction with calibration
3. **Confidence Calculation**: Confidence scores from probabilities
4. **Regime Classification**: HTF regime detection (trend/range/balanced)
5. **Decision Making**: Final trading decision with risk management
6. **Exit Logic**: HTF Fibonacci exits with partial exits and trailing

### Feature Computation Modes

**CRITICAL**: Genesis-Core has two feature computation paths with different semantics:

1. **Live Trading** (`features.py::extract_features`):
   - Assumes current bar is forming (not closed)
   - Uses bars 0 to `now_index-1` (excludes current bar)

2. **Backtesting** (`indicators/vectorized.py::calculate_all_features_vectorized`):
   - All bars are historical (closed)
   - Uses all bars including current

**Canonical Mode (for quality decisions)**:

- `GENESIS_FAST_WINDOW=1` (NumPy views for performance)
- `GENESIS_PRECOMPUTE_FEATURES=1` (on-disk feature cache)
- These are required for Optuna, validation, champion comparison, and reporting

**Debug Mode (0/0)**: Allowed for troubleshooting but NOT comparable to canonical results. Requires `GENESIS_MODE_EXPLICIT=1`.

### Configuration Management

**Runtime Config SSOT** (`config/runtime.json`):

- Seeded from `config/runtime.seed.json`
- Modified via API: `POST /config/runtime/propose` (requires Bearer token)
- Validated via API: `POST /config/runtime/validate`
- Audit trail in `logs/config_audit.jsonl`

**Model Registry** (`config/models/`):

- Separate from governance registry
- Stores ML models per symbol/timeframe
- Includes weights, calibration, schema, version

**Champion Configs** (`config/strategy/champions/`):

- Best-performing strategy configurations
- Includes `merged_config` for reproducibility
- Loaded by `ChampionLoader` in pipeline

### Registry Governance

Located under `registry/`:

- `.github/skills/*.json` - Versionized skills
- `registry/compacts/*.json` - Versionized compacts
- `registry/manifests/dev.json` and `stable.json` - Active versions
- `registry/schemas/*.schema.json` - JSON Schema definitions

**CI Gate**: `python scripts/validate_registry.py` validates schema + cross-references

### Bounded Agents

Repo-local agents under `.github/agents/`:

- **Plan** - Create testable plans for large/ambiguous tasks (no implementation)
- **AnalysisAudit** - Read-only audit of logic, gates, scoring (no runs, no changes)
- **GovernanceQA** - Registry/skills/compacts validation, lint/test/security gates
- **OpsRunner** - Run backtests/Optuna reproducibly with canonical mode defaults

## Critical Development Rules

### Execution Mode Policy

- **Canonical mode (1/1)** is REQUIRED for all quality decisions:
  - Optuna optimization
  - Validation runs
  - Champion comparisons/promotion
  - Any reporting used for decisions
- Debug mode (0/0) is allowed ONLY for troubleshooting and requires `GENESIS_MODE_EXPLICIT=1`
- Never compare results from different modes

### Determinism

- `GENESIS_RANDOM_SEED=42` is set by runner if not specified
- Reproducibility is verified via double-runs
- All backtest artifacts include `execution_mode`, `git_hash`, `seed`, and `timestamp`

### Security

- NEVER commit: `.env`, `.nonce_tracker.json`, `dev.overrides.local.json`
- API keys ONLY from environment variables
- Paper trading MUST use TEST symbols (enforced in code)
- JSON signing uses compact format: `json.dumps(body, separators=(",",":"))`

### Code Standards

- Python 3.11+ syntax (modern typing: `dict` not `Dict`, `X|None` not `Optional[X]`)
- Line length: 100 characters
- Style: `black` formatting, `ruff` linting
- Testing: `pytest` with comprehensive coverage
- No emojis in source files

### Git Workflow

- NEVER update git config
- NEVER run destructive git commands without explicit user request
- ALWAYS create NEW commits (not amend) unless explicitly requested
- Stage specific files by name (avoid `git add -A` or `git add .`)
- Commit message format: End with `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### Stability Policy

**Code stability > New features**. Every line must either:

- ✅ Solve a concrete problem, OR
- ✅ Increase reliability, performance, or readability

**Change Policy:**

- Bug fixes: ✅ Always allowed (write test immediately)
- Refactoring: ✅ Small, documented steps without behavior change
- New features: ⚠️ Only after clear specification and justification
- Experimental: 🚫 Separate branch only

### Over-Engineering Prevention

- Only make changes directly requested or clearly necessary
- Don't add features, refactoring, or "improvements" beyond what was asked
- Don't add error handling for scenarios that can't happen
- Don't create abstractions for one-time operations
- Three similar lines > premature abstraction

## Common Workflows

### Optimization Flow (Coarse → Fine)

1. **Preflight Check** (ALWAYS before long runs):

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

2. **Smoke Test** (quick validation):

```powershell
# 5-10 trials on short window to verify config
```

3. **Explore** (broad search):

```powershell
# 30-60 trials, short window (H1 2024)
# Wider parameter ranges to find promising regions
```

4. **Validate** (strict evaluation):

```powershell
# Top-N from explore, long window (FY 2024)
# Stricter constraints, full evaluation
```

5. **Analyze Results**:

```powershell
python scripts/optimizer.py summarize run_<ID> --top 10
python scripts/analyze_optuna_db.py <path_to_db>
```

6. **Update Champion** (if validated):

```powershell
# Manually update config/strategy/champions/<symbol>_<tf>.json
# Document in docs/daily_summaries/daily_summary_YYYY-MM-DD.md
```

### Git LFS Policy

- Use Git LFS ONLY for curated result bundles (Policy B)
- Location: `results/archive/bundles/*.zip` (tracked via `.gitattributes`)
- Do NOT LFS-track raw `results/**`, `*.db`, or `cache/**`
- Bundles must be minimal and reproducible (config + summary, no secrets)

## FastAPI Endpoints

- `/ui` - Trading dashboard
- `/strategy/evaluate` - Run strategy pipeline
- `/public/candles` - Fetch market data
- `/auth/check` - Verify authentication
- `/paper/submit` - Submit paper orders (TEST symbols only)
- `/debug/auth` - Debug auth issues
- `/health` - Health check
- `/metrics` - Prometheus metrics
- `/account/wallets`, `/account/positions`, `/account/orders` - Account proxies
- `/config/runtime` - Get SSOT config
- `/config/runtime/validate` - Validate config
- `/config/runtime/propose` - Propose changes (Bearer auth)

## Troubleshooting

### Common Issues

**"invalid key" error**: Check JSON serialization consistency (use compact format)

**"Ingen giltig order"**: Verify model exists for symbol/timeframe, check risk config

**Nonce errors**: Use `bump_nonce()` for retry

**Zero trades in backtest**: Check decision logging for gate reasons (HTF/LTF fib, hysteresis, thresholds)

**Optuna duplicate trials**:

- Widen search space (lower entry thresholds)
- Use `bootstrap_random_trials` for initial exploration
- Check that all YAML leaf nodes have `type: fixed|grid|float|int|loguniform`

**Optimizer results don't match manual backtest**:

- Verify same execution mode (`GENESIS_FAST_WINDOW`, `GENESIS_PRECOMPUTE_FEATURES`)
- Check `warmup_bars` alignment
- Use `scripts/check_trial_config_equivalence.py` for drift detection

### Debugging Steps

1. Check relevant logs in `logs/` directory
2. Run single backtest with detailed logging: `LOG_LEVEL=DEBUG python scripts/run_backtest.py ...`
3. Use diagnostic scripts: `scripts/diagnose_*.py`
4. Verify config validity: `scripts/validate_optimizer_config.py`
5. Check execution mode in backtest artifacts (`backtest_info.execution_mode`)

## Key Implementation Details

### SymbolMapper

- `SYMBOL_MODE`: `realistic|synthetic` (env var, CI sets `synthetic`)
- Realistic: `BTCUSD` → `tBTCUSD`
- Synthetic: `BTCUSD` → `tTESTBTC:TESTUSD`
- Explicit TEST symbols bypass mapping

### HTF Fibonacci Exits

- Higher timeframe (1D) swing detection
- Exit levels: 0.382, 0.5, 0.618, 0.786
- Partial exits at configurable thresholds
- Trailing stop based on ATR multiplier
- Fallback to confidence-based exits when HTF unavailable

### Decision Flow Gates

Decision logging shows why entries are blocked:

- `EV_BLOCK`: Expected value too low
- `PROBA_BLOCK`: Probability below threshold
- `EDGE_BLOCK`: Edge insufficient
- `HTF_FIB_BLOCK`: HTF Fibonacci gate rejection
- `LTF_FIB_BLOCK`: LTF Fibonacci gate rejection
- `HYSTERESIS`: Recent opposite signal
- `COOLDOWN`: Recent trade cooldown period

### Import Convention

Active scripts should use:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import core.<module>  # NOT src.core.<module>
```

## Important Files

**Strategy Core:**

- `src/core/strategy/features_asof.py` - Feature extraction for backtesting
- `src/core/strategy/decision.py` - Trading decision logic with gates
- `src/core/strategy/evaluate.py` - Complete evaluation pipeline
- `src/core/backtest/engine.py` - Backtest execution engine

**Indicators:**

- `src/core/indicators/fibonacci.py` - Fibonacci swing detection
- `src/core/indicators/htf_fibonacci.py` - Higher timeframe Fibonacci
- `src/core/indicators/vectorized.py` - Vectorized indicator calculations

**Optimization:**

- `src/core/optimizer/runner.py` - Optuna runner with resume safety
- `src/core/optimizer/champion.py` - Champion management

**Configuration:**

- `src/core/config/schema.py` - Config schema validation
- `src/core/pipeline.py` - Unified pipeline with canonical mode enforcement

**Documentation:**

- `AGENTS.md` - Detailed agent workflow and deliverables history
- `README.md` - Quick start guide (Swedish)
- `docs/features/FEATURE_COMPUTATION_MODES.md` - Feature computation deep dive
- `docs/optuna/` - Optuna best practices and troubleshooting

## MCP Server Integration

The repo includes an MCP (Model Context Protocol) server for AI assistant integration:

```powershell
python -m pip install -e ".[mcp]"
python -m mcp_server.server
```

See `mcp_server/README.md` and `docs/mcp_server_guide.md` for details.

## Language Preference

Prefer Swedish responses unless specified otherwise (per workspace rules in `.cursor/rules/`).
