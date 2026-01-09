# Changelog

All notable changes to Genesis-Core are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed - Security & CI hardening (2026-01-09)

- Sanitized client-facing error payloads to avoid leaking exception details (CodeQL: information exposure through an exception).
  - FastAPI endpoints now return stable error codes (and `error_id` where applicable) while logging the full exception server-side.
  - HTF/feature meta no longer embeds exception strings.
  - Added regression tests to ensure exceptions are not echoed in HTTP responses.
- CI workflow now sets explicit `permissions` for `GITHUB_TOKEN` (least privilege) to satisfy CodeQL
  (`actions/missing-workflow-permissions`).

### Changed - Phase-8 (2026-01-08)

**Documentation continuity (MCP + Optuna + dev setup)**

- Updated `docs/dev_setup.md` to be a practical dev setup SSOT (venv/deps/QA) and kept editor baseline as a separate section.
- Updated `docs/roadmap/STABILIZATION_PLAN_9_STEPS.md` to reflect current implementation status (pipeline/defaults/canonical mode).
- Updated `docs/mcp_server_guide.md` with a short TL;DR and clearer recommendation: local stdio server in VS Code by default; remote HTTP server only when needed.
- Removed provider-specific tunnel/hostname examples from `mcp_server/README.md` and replaced them with provider-agnostic reverse-proxy/port-forwarding guidance.
- Updated Optuna docs for Windows: `docs/optuna/OPTUNA_BEST_PRACTICES.md` and `docs/optuna/README.md` now include PowerShell-friendly environment variable examples and a minimal smoke workflow.
- Repurposed `scripts/debug_mcp_tunnel.py` to a simple `/healthz` reachability check for the remote MCP server.

### Changed - Phase-8 (2026-01-02)

**Optimization & Metrics**

- Fixed metrics reporting bug in `src/core/backtest/metrics.py` (specifically `calculate_backtest_metrics`) to ensure accurate `total_trades` and `total_return` are reported during parameter optimization.
- Resolved issue where optimization trials failed to capture correct trade counts, enabling successful tuning of `HTFFibonacciExitEngine`.

### Changed - Phase-7d (2025-11-10)

**Scoring & Constraints**

- Score beräknar PF/DD från trades/equity via `core.backtest.metrics.calculate_metrics`. Slutar att förlita sig på `summary` för dessa fält.
- `return_to_dd` skyddas mot noll‑DD.
- Constraints och scoringens “hard_failures” separerade. Ny YAML‑flagga `include_scoring_failures` styr om scoringens hårda fel ska behandlas som constraints‑skäl.

**Runner & Determinism**

- Runner exporterar `GENESIS_RANDOM_SEED=42` till backtest‑subprocesser om inte redan satt (reproducerbarhet).
- Miljöflaggor för prestanda: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1` (aktiverar NumPy‑views och förberäknade features/cacher).

**Backtest Summary**

- `PositionTracker.get_summary()` rapporterar korrekt `profit_factor` (gross_profit/gross_loss) och inkluderar `max_drawdown` beräknat från equity‑kurvan.

**Optimizer Config (Fib‑Tune)**

- Breddad sökrymd för entry/tolerans/override (fler trades i utforskning).
- Mildare constraints i YAML: `min_trades: 3`, `min_profit_factor: 0.8`, `max_max_dd: 0.35`.
- TPE-sampler med `constant_liar: true`, `multivariate: true`, `n_ei_candidates: 512`.

**Documentation**

- `docs/optimizer.md`: ny sektion om robust scoring, constraints‑separation, YAML‑schema för bladnoder, prestandaflaggor, determinism.
- `docs/features/FEATURE_COMPUTATION_MODES.md`: ny sektion om fast‑window och precompute.
- `docs/daily_summaries/daily_summary_2025-11-10.md`: dagens summering.
- `AGENTS.md`: uppdaterad snabbguide och deliverables.

**Fixes**

- Eliminering av NumPy “truth value is ambiguous” i fast‑window path (säker sanningskontroll för arrayer i features/regime).

### Changed - Phase-7d (2025-11-11)

**Optuna Search Space & Bootstrap**

- `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml` breddad: större intervall för `entry_conf_overall`, `regime_proba`, `min_edge`, `exit_conf_threshold`, `max_hold_bars`, fler `risk_map`-alternativ (inkl. championens exakta map), samt gridade boolska flippar för HTF/LTF-gates och overrides.
- Tillagt `bootstrap_random_trials: 32` + `bootstrap_seed: 42` för en deterministisk RandomSampler-fas innan TPE (korrelerad med `GENESIS_MAX_CONCURRENT=4`).

**Runner Logic**

- `_run_optuna()` kör nu bootstrap-fasen via separat studie (RandomSampler) innan huvudstudien laddas med TPE. Soft-constraint-straff ändrat från `score - 1e6` till `score - 1e3` for bättre rankningssignal.

**Validation & Smoke Run**

- Preflight/validator uppdaterad (nytt `study_name`/`storage`-timestamp) och champion risk-map kontrolleras mot nya grid-listan.
- Smoke-run `run_20251111_134030` (32 bootstrap + 48 TPE) gav score `0.8473`, 99 trades. TPE-fasen har fortfarande hög duplicatfrekvens (~98.8%) → fortsätt öppna upp toleranser, sänk `ltf_override_threshold` och bevaka zero-trade ratio.

**Documentation**

- `AGENTS.md`: uppdaterade deliverables, snabbguide (concurrency 4 + bootstrap-tip), och statusrapport för duplicat-åtgärder.

### Changed - Phase-7d (2025-11-18)

**Dokumentation & Struktur**

- Performance-guiden och analysen flyttades till `docs/performance/` (nu inkluderar de även Phase-6-insikterna via collapsible-detaljer).
- Optuna-dokumenten (`OPTUNA_OPTIMIZATIONS.md`, `OPTUNA_OPTIMIZATION_ANALYSIS.md`) placerades i `docs/optuna/` medan `DATA_STORAGE_STRATEGY.md` fick ett dedikerat `docs/data/`-hem och `OPTIMIZATION_SUMMARY.md` flyttades till `docs/optimization/`.
- Samtliga gamla Phase-6-dokument (`README.md`, `TODO.md`, `PHASE-6_LEARNINGS.md`, `DOCUMENTATION_ANALYSIS.md`, `ORIGINAL_REPO_MENTIONS.md`) arkiverades under `docs/archive/phase6/` för att hålla huvudträdet rent.

**Benchmarks & Rapporter**

- `scripts/benchmark_performance.py --bars 2000 --iterations 10 --export reports/benchmark_results.json` kördes om; både JSON-exporten och `reports/PERFORMANCE_BENCHMARK_RESULTS.md` uppdaterades med de nya 266.9 ms totalsiffrorna.

**Miljöspårning**

- Ny `pip freeze`-snapshot (`reports/pip_freeze_20251118.txt`) genererades från den aktiva `.venv`-miljön för att spegla Phase-8-dependenser.

### Added - HTF Fibonacci Exit System (2025-10-13)

**Major Feature: Dynamic Exit Strategy**

- Implemented HTF (Higher Timeframe) Fibonacci-based exit logic
- Replaces fixed TP/SL with market structure-aware exits
- Uses 1D swings projected to 1h timeframe decisions

**New Modules:**

- `src/core/indicators/htf_fibonacci.py` - HTF Fibonacci calculation with AS-OF semantics
- `src/core/backtest/htf_exit_engine.py` - Core exit engine with partial/trail/structure logic

**Enhanced Modules:**

- `src/core/backtest/position_tracker.py` - Partial exit infrastructure

  - Added `Position.current_size`, `initial_size`, `partial_exits` tracking
  - Added `Trade.is_partial`, `exit_reason`, `remaining_size`, `position_id`
  - New `partial_close()` method for fractional position closing

- `src/core/backtest/engine.py` - HTF exit integration

  - Integrated `HTFFibonacciExitEngine` with configurable thresholds
  - Added HTF context extraction from feature pipeline
  - Fixed trade serialization (added exit metadata)

- `src/core/strategy/features.py` - HTF context in feature extraction
  - Added `get_htf_fibonacci_context()` call
  - HTF levels available in `meta['htf_fibonacci']`

**Exit Logic Features:**

1. **Partial Exits:** TP1 @ 0.382 Fib (40%), TP2 @ 0.5 Fib (30%)
2. **Trailing Stop:** EMA-based with HTF promotion (locks at 0.5 Fib)
3. **Structure Break:** Full exit on 0.618 break + momentum loss
4. **Adaptive Thresholds:** Dynamic ATR+% proximity calculation
5. **Reachability Check:** 8 ATR envelope prevents stale swing usage
6. **Fallback Logic:** EMA-trail when HTF unavailable

**Verification Results (tBTCUSD 1h, 2025-08-01 to 2025-10-13):**

- 7 total trades, 2 partial exits (28.6%), 5 full exits
- Partial exits correctly triggered at HTF Fibonacci levels
- Fallback logic engaged when HTF swings out of reach
- All integration tests passing

**Data Updates:**

- Fresh data fetched: tBTCUSD 1D (6 months), 1h (3 months)
- Stored in curated + legacy structures for compatibility

**Bug Fixes:**

- Fixed dict vs float ATR extraction error
- Removed null bytes causing SyntaxError
- Corrected HTF context nesting in pipeline
- Added missing trade fields to results serialization

**Documentation:**

- `docs/fibonacci/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` - Complete implementation guide

**Test Coverage:**

- `scripts/test_htf_fibonacci_mapping.py` - HTF mapping tests
- `scripts/test_partial_exit_infrastructure.py` - Partial exit tests
- `scripts/test_htf_exit_engine.py` - Integration tests
- `scripts/debug_htf_exit_usage.py` - Debug verification

**Status:** ✅ Production ready, ablation study pending

---

### Strategic Decision Needed

- Bitcoin 1h timeframe shows mean reversion behavior (trend features have NEGATIVE IC)
- System is production-ready, but strategy direction needs confirmation
- Options: Test 4h/1D timeframes, optimize mean reversion, or research new approaches

---

## [0.6.0] - 2025-10-10 (Phase-6c COMPLETE)

### 🚨 CRITICAL BUG FIX - Phase-6a

**Bollinger Bands Standard Deviation Bug:**

- **Problem:** Vectorized BB calculation used `ddof=1` (sample std), per-sample used `ddof=0` (population std)
- **Impact:** 1.21% systematic error in `bb_position_inv_ma3` feature
- **Result:** ALL features and models from before 2025-10-10 were INVALID
- **Fix:** Changed `std(ddof=1)` → `std(ddof=0)` in `src/core/indicators/vectorized.py`
- **Validation:** Bit-exact parity achieved (max diff 3.44e-10)

### Added - Phase-6a

- **Systematic Indicator Validation Framework:**

  - `scripts/validate_all_indicators.py` - Permanent quality gate
  - Validates per-sample vs vectorized implementations
  - Cross-validates with TA-Lib (if available)
  - Tests: EMA, RSI, ATR, Volatility Shift - ALL machine precision ✅

- **Data Integrity Validation:**
  - `scripts/validate_candle_integrity.py` - Comprehensive data quality checks
  - `scripts/inspect_candle_data.py` - Quick data inspection
  - Validated tBTCUSD 1h: 93.75% integrity, authentic Bitfinex data ✅

### Added - Phase-6b

- **Comprehensive Feature Analysis:**
  - `scripts/comprehensive_feature_analysis.py` - Test 25 features across regimes
  - Discovered: Bitcoin 1h is MEAN REVERSION market (trend features negative IC!)
  - Identified: Volatility features strongest (IC +0.25 in Bear regime)

### Added - Phase-6c

- **Regime-Aware ML Calibration:**

  - `scripts/analyze_calibration_by_regime.py` - Analyze ML calibration per regime
  - `scripts/calibrate_by_regime.py` - Regime-specific Platt scaling
  - `src/core/strategy/regime_unified.py` - Unified regime detection (EMA-based)
  - Integrated regime-aware calibration into `predict_proba_for()`
  - Result: Bear regime boost a=4.15 (+18% probability!)

- **Documentation:**
  - `docs/PHASE-6_LEARNINGS.md` - Complete Phase-6 discoveries and learnings
  - `docs/README.md` - Documentation manifest (active vs archived)
  - `results/README.md` - Results directory guide with key findings

### Changed - Phase-6

- **Pipeline Integration:**

  - `src/core/strategy/evaluate.py` - Now detects regime BEFORE ML prediction
  - `src/core/strategy/prob_model.py` - Applies regime-specific calibration parameters
  - `src/core/strategy/features.py` - Refactored to v15 (5 non-redundant features)

- **Configuration:**

  - `config/runtime.json` - Added regime-specific probability thresholds
  - `config/models/tBTCUSD_1h.json` - Updated with regime calibration parameters

- **Feature Set Evolution:**
  - v12: 6 IC-selected features (inverted for positive IC)
  - v15: 5 non-redundant features optimized for mean reversion
    - rsi_inv_lag1, volatility_shift_ma3, bb_position_inv_ma3, rsi_vol_interaction, vol_regime

### Fixed - Phase-6

- **Critical Bugs:**

  - Bollinger Bands `ddof` parameter (1.21% systematic error) 🚨
  - Unicode encoding errors in Windows console output
  - JSON serialization errors (numpy.bool\_, numpy.int32)
  - Mutable default arguments in multiple functions

- **Data Issues:**
  - Removed all features generated before BB fix (safety cleanup)
  - Removed meta_labels based on wrong features

### Removed - Phase-6

- **Outdated Files:**
  - Old features from 15m, 1m, ETH (generated with wrong BB)
  - Old meta_labels (based on wrong features)
  - Archived 162 experiment files → `results/archive_2025-10-09/`
  - Archived 5 legacy docs → `docs/archive/`

### Performance - Phase-6c

**Model: tBTCUSD_1h_v3.json**

- IC @ 20-bar: +0.0528 (EXCELLENT, p<0.001, ICIR 0.51)
- Bear regime: IC +0.0946, 58.6% win rate, calib boost a=4.15
- Bull regime: IC +0.0124 (NOT significant), blocked by high threshold (0.90)
- Ranging: IC +0.0456, normal behavior, threshold 0.50

**Data Quality:**

- Candle integrity: 93.75% (GOOD)
- Source: Bitfinex REST API v2 (authentic market data)
- ATR: 0.57% median (realistic for BTC)
- Zero flat bars, minimal gaps

**System Health:**

- 334/334 tests passing
- All indicators validated (machine precision)
- Clean codebase (Ruff + Black + Bandit)

### QA/Tests - Phase-6

- ✅ 334 tests passing (100% pass rate)
- ✅ Black formatting: 100%
- ✅ Ruff linting: 0 errors
- ✅ Bandit security: 0 critical
- ✅ All indicators validated (bit-exact parity)
- ✅ Data integrity confirmed (93.75%)

---

## [0.5.0] - 2025-10-09 (Phase-5 COMPLETE)

### Added - Phase-5

- **Centralized Feature Loading:**

  - `src/core/utils/data_loader.py` - Single source for feature loading
  - Smart format selection (Feather first for speed, fallback to Parquet)
  - Robust error handling with helpful messages

- **Champion Decision Matrix:**

  - `src/core/ml/decision_matrix.py` - Systematic model comparison
  - `ModelMetrics` dataclass for model performance encapsulation
  - Flexible weighting system (balanced, conservative, aggressive, quality)
  - Normalized scoring and ranking

- **Visualization:**

  - `src/core/ml/visualization.py` - Visual model comparison
  - Radar charts for multi-metric comparison
  - Comprehensive summary plots
  - Integration with `scripts/select_champion.py`

- **Advanced Validation Infrastructure:**

  - `scripts/validate_purged_wfcv.py` - Purged Walk-Forward Cross-Validation
  - `src/core/utils/provenance.py` - Deterministic hashing for reproducibility
  - `scripts/monitor_feature_drift.py` - PSI and K-S drift detection
  - `src/core/ml/overfit_detection.py` - Deflated Sharpe, PBO
  - `scripts/validate_regime_gates.py` - Regime-specific performance gates

- **Configuration:**

  - `config/validation_config.json` - Centralized validation parameters
  - `config/champion_weights.json` - Weight profiles for model selection

- **IC Metrics & Analysis:**

  - `scripts/calculate_ic_metrics.py` - Information Coefficient analysis
  - `scripts/analyze_quintiles.py` - Quintile analysis for predictions
  - `scripts/fdr_correction.py` - False Discovery Rate correction
  - `scripts/calculate_ic_by_regime.py` - Regime-split IC analysis
  - `scripts/calculate_partial_ic.py` - Feature synergy detection

- **Feature Engineering:**

  - `src/core/indicators/macd.py` - MACD indicator
  - Expanded feature set to 15 features (reactivated FVG, added classical indicators)

- **Documentation:**
  - `docs/ADVANCED_VALIDATION_PRODUCTION.md` - Production ML guide (2,045 lines)
  - `docs/INDICATORS_REFERENCE.md` - Technical indicators reference (847 lines)
  - `.cursor/rules/` - Hierarchical rule structure with README

### Changed - Phase-5

- **Updated Scripts:**

  - All ML scripts now use `core.utils.data_loader.load_features()`
  - `scripts/select_champion.py` - Integrated ChampionDecisionMatrix & visualization
  - `scripts/train_model.py` - Added `--use-holdout` and `--save-provenance` flags

- **Test Updates:**

  - Updated all tests to mock both `scripts.train_model.Path` and `core.utils.data_loader.Path`
  - Updated `split_data_chronological` tests for new `holdout_indices` return value

- **Documentation:**
  - Consolidated rules into hierarchical structure (`cursor-active-rules.mdc`, `reference-guide.md`)
  - Removed redundant `CURSOR_RULES.txt`
  - Archived `ROBUSTNESS_IMPLEMENTATION_GUIDE.md` (superseded)

### Fixed - Phase-5

- Ruff linting errors (ambiguous variable names, bare except)
- Black formatting issues (unnecessary f-strings)
- Test mocking issues (Path objects not correctly mocked)
- `KeyError: 'total_score'` in empty models dictionary
- Ruff issues in visualization.py (dict() call, zip() strict, unused variables)

### QA/Tests - Phase-5

- ✅ 307 tests passing
- ✅ Black formatting: 100%
- ✅ Ruff linting: 0 errors
- ✅ 15 new tests for decision matrix
- ✅ 12 new tests for visualization

---

## [0.4.0] - 2025-10-08 (Phase-4 COMPLETE)

### Added - Phase-4

**E2E Strategy Pipeline:**

- `src/core/strategy/evaluate.py` - Complete orchestration pipeline
  - Feature extraction → ML prediction → Confidence → Regime → Decision
  - Comprehensive metadata tracking
  - Health checks and error handling
  - Integration tests
  - FastAPI endpoint: `POST /strategy/evaluate`

**Observability & Monitoring:**

- `src/core/observability/` - Complete observability framework
  - `metrics.py` - Prometheus metrics (30+ metrics)
  - `health.py` - Health checks (6 checks: API, features, model, config, regime, decision)
  - `audit.py` - Audit logging with rotation
  - FastAPI endpoints: `/health`, `/metrics`

**Dashboard:**

- `ui/index.html` - Real-time trading dashboard
  - Live strategy evaluation
  - Candlestick charts (lightweight-charts)
  - Feature visualization
  - Probability gauges
  - Trade history table
  - Performance metrics

**Paper Trading:**

- `src/core/paper/` - Paper trading simulation
  - Virtual wallet management
  - Order submission (TEST symbols only)
  - Position tracking
  - Commission/slippage simulation
  - FastAPI endpoints: `/paper/submit`, `/paper/estimate`, `/paper/whitelist`

**Account & Market Data:**

- FastAPI endpoints for account info:
  - `GET /account/wallets` - Wallet balances
  - `GET /account/positions` - Active positions
  - `GET /account/orders` - Order history
- Public market data:
  - `GET /public/candles` - Historical OHLCV data

**Development Tools:**

- `GET /debug/auth` - Test REST authentication
- `POST /models/reload` - Force clear model cache

### Changed - Phase-4

- **ModelRegistry:** Exact mtime-match for cache invalidation (critical for ML)
- **FastAPI:** Migrated from `@app.on_event` to `lifespan` context manager
- **HMAC signature:** Refactored to shared `src/core/utils/crypto.py` utility (DRY)
- **Model structure:** All 16 symbols use multi-timeframe structure

### Fixed - Phase-4

- Cache invalidation preventing ML models from reloading
- HMAC signature duplication (4 places → 1 utility)
- FastAPI deprecation warnings
- 27 linting issues (ruff auto-fix + manual fixes)

### QA/Tests - Phase-4

- ✅ 115/115 tests passing
- ✅ Black formatting: 100%
- ✅ Ruff linting: 0 errors
- ✅ Bandit security: 0 critical

---

## [0.3.0] - 2025-10-08 (Phase-3 COMPLETE)

### Added - Phase-3

**ML Training Pipeline:**

- `scripts/precompute_features.py` - Batch feature extraction
- `src/core/ml/labeling.py` - Binary and multiclass label generation
- `scripts/train_model.py` - Logistic Regression training with GridSearchCV
- `scripts/evaluate_model.py` - Comprehensive model evaluation
- `scripts/calibrate_model.py` - Probability calibration (Platt, Isotonic)
- `scripts/select_champion.py` - Automated model selection

**Feature Engineering:**

- `src/core/indicators/bollinger.py` - Bollinger Bands (23 tests)
- `src/core/indicators/volume.py` - Volume analysis (36 tests)
- Enhanced regime detection (Bull/Bear/Ranging/Balanced)
- 11-feature extraction (EMA, RSI, ATR, BB, ADX, Volume, OBV)

**Triple-Barrier Labeling:**

- Fixed threshold labels (profit/stop/time barriers)
- Adaptive ATR-based labels (volatility-aware)
- Noise filtering (small moves → None labels)

**Confidence & Edge Filtering:**

- Min edge requirement in decision logic
- Configurable via `cfg["thresholds"]["min_edge"]`

### Results - Phase-3

**Champion Model: v3_adaptive_6m**

- AUC: 0.5987 (+15.8% vs baseline 0.517)
- Features: 11
- Labeling: Adaptive triple-barrier (1.5x/1.0x ATR)
- Data: 6 months recent (2,280 samples)
- Quality over quantity validated

### QA/Tests - Phase-3

- ✅ 270 tests passing
- ✅ 93 new tests (Bollinger, Volume, Triple-barrier, Edge filter)
- ✅ Code quality: Black, Ruff, Bandit all clean

---

## [0.2.0] - 2025-10-07 (Phase-2 COMPLETE)

### Added - Phase-2

**Backtest Framework:**

- `BacktestEngine` - Bar-by-bar historical replay
- `PositionTracker` - PnL tracking with commission/slippage
- `Metrics` - Sharpe, max DD, win rate, profit factor, Sortino, Calmar
- `TradeLogger` - Export to JSON/CSV
- `scripts/run_backtest.py` - CLI backtest runner
- 28 comprehensive tests

**Data Foundation:**

- `scripts/fetch_historical.py` - Historiska candles från Bitfinex (Parquet)
- `scripts/validate_data.py` - Datakvalitetsvalidering
- Kuraterad struktur: `data/curated/v1/candles/` (aktiva datasets), `data/raw/bitfinex/`, `data/metadata/curated/`
- Äldre data hålls i `data/archive/`
- Initial data: tBTCUSD/tETHUSD 15m/1h, 3 månader, 99.9%+ kvalitet

**API Improvements:**

- `GET /paper/estimate` - Calculate min/max order size (wallet-aware)
- `GET /paper/whitelist` - List TEST symbols for paper trading
- `POST /models/reload` - Force clear model cache

**Utilities:**

- `src/core/utils/crypto.py` - Shared HMAC signature building (DRY)

### Changed - Phase-2

- ModelRegistry cache: Exact mtime-match (critical for ML)
- FastAPI: Modern `lifespan` context manager (no deprecation warnings)
- HMAC: Refactored from 4 duplicates to 1 utility

### Fixed - Phase-2

- Cache invalidation blocking ML model reloads
- HMAC signature duplication
- FastAPI deprecation warnings
- 27 linting issues

### QA/Tests - Phase-2

- ✅ 115/115 tests passing
- ✅ Black: 100%, Ruff: 0 errors, Bandit: 0 critical
- ✅ Comprehensive code review documented

---

## [0.1.0] - 2025-10-03 (Phase-1 COMPLETE)

### Added - Phase-1

**SSOT Runtime Config API:**

- `GET /config/runtime` - Read current config
- `POST /config/runtime/validate` - Validate config changes
- `POST /config/runtime/propose` - Propose changes (optimistic locking)
- Bearer auth for config changes (`BEARER_TOKEN` env var)
- Audit logging with rotation (`logs/config_audit.jsonl`)
- Config seeding from `config/runtime.seed.json` on first start

**Strategy Pipeline:**

- Feature extraction (EMA, RSI)
- Probability model (buy/sell predictions)
- Confidence scoring
- Regime detection (Bull/Bear/Ranging/Balanced)
- Decision logic (EV-based, gates, hysteresis)

**UI Improvements:**

- Config version/hash display in status panel
- Bearer token input for config proposals
- `localStorage.ui_bearer` token persistence

**Symbol Mapping:**

- `SymbolMapper` - Normalize between human (`BTCUSD`) and Bitfinex (`tBTCUSD`)
- Supports `SYMBOL_MODE=realistic|synthetic` via env var

### Removed - Phase-1

- Legacy config endpoints (`/config/validate`, `/config/diff`, `/config/audit`)
- Old ad-hoc override flows

### Migration - Phase-1

**Config API Migration:**

- Read: `GET /config/runtime` → `{ cfg, version, hash }`
- Validate: `POST /config/runtime/validate` with full config
- Propose: `POST /config/runtime/propose` with `{ patch, actor, expected_version }` and `Authorization: Bearer <token>`

### QA/Tests - Phase-1

- E2E tests for config API (401 without Bearer, success with Bearer)
- Unit tests for SymbolMapper and integration in REST/WS

---

## Archive

**Pre-Phase-6 documentation:** See `docs/archive/CHANGELOG_pre-phase6.md`

**Pre-Phase-3 TODOs:** See `docs/archive/TODO_*_superseded.md`

---

## Version History Summary

| Version | Date       | Phase | Key Achievement                                                   |
| ------- | ---------- | ----- | ----------------------------------------------------------------- |
| 0.6.0   | 2025-10-10 | 6c    | 🚨 BB bug fix, regime-aware calibration, mean reversion discovery |
| 0.5.0   | 2025-10-09 | 5     | Advanced validation, champion matrix, IC metrics                  |
| 0.4.0   | 2025-10-08 | 4     | E2E pipeline, observability, dashboard, paper trading             |
| 0.3.0   | 2025-10-08 | 3     | ML pipeline, 11 features, triple-barrier, AUC 0.5987              |
| 0.2.0   | 2025-10-07 | 2     | Backtest framework, data foundation                               |
| 0.1.0   | 2025-10-03 | 1     | SSOT config, strategy pipeline, symbol mapping                    |

---

**Current Status:** ✅ Production-ready system | ⚠️ Strategy decision needed (trend vs mean reversion)
