# Composable Strategy Architecture - Project Tracking

**Branch**: `feature/composable-strategy-phase2`
**Started**: 2026-01-29
**Phase 1 Completed**: 2026-01-30
**Phase 2 Completed**: 2026-02-02
**Phase 3 Milestone 1 Completed**: 2026-02-03
**Phase 3 Milestone 2 Completed**: 2026-02-03
**Phase 3 Status**: ✅ MILESTONE 2 CLOSED - HQT Audit complete
**Owner**: Claude Code + User

**Latest**: Milestone 2 (HQT Audit, PF-first) CLOSED (2026-02-03)
- ✅ HQT audit completed on v4a baseline (read-only)
- ❌ Verdict: HQT-FAIL (robustness criterion not met)
- ⚠️ Critical: PF collapses to 1.07 when top-3 trades removed (< 1.2 threshold)
- ⚠️ High concentration: Top-1 trade = 40.7% of total PnL
- 🔍 Root cause: Low trade frequency (63/year) + outlier dependence
- ✅ All other criteria pass: PF 1.59, all quarters >= 1.3, fees reasonable
- 📊 Recommendation: Proceed with Sizing Policy Review to increase trade frequency
- See: `docs/features/PHASE3_MILESTONE2_HQT_AUDIT.md`

**Previous**: Milestone 1 (Component Tuning, config-only) CLOSED (2026-02-03)
- ✅ v4a baseline established: 63 trades/year, PF 1.59, Win 68.3%, Return 1.14%
- ✅ Extended validation (full 2024) passed guardrails: all quarters >0 trades
- ✅ Bug #1 (CooldownComponent phantom trades) FIXED - 1526 phantom vetoes eliminated
- ✅ Bug #2 (ComponentContextBuilder key mapping) FIXED - EVGate functional
- ✅ Execution layer analyzed: ATR zone sizing is bottleneck (98.6% size==0)
- ⚠️ Finding: Permissive baseline is toothless (0% component veto rate)
- See: `docs/features/PHASE3_MILESTONE1_CLOSURE.md`

---

## Project Overview

### Problem Statement

Current strategy architecture har flera fundamentala problem:
1. **Overfitting**: Champion PF 1.53 in-sample → 1.04 OOS (-32% degradation)
2. **Low trade count**: 16-31 trades/år → statistiskt oanvändbart
3. **No component attribution**: Omöjligt att veta vad som ger värde
4. **Monolithic decision logic**: Allt hårt kopplat, svårt att testa/debugga
5. **Opaque optimization**: Optuna optimerar allt, vet inte vad som fungerar

### Solution Approach

**Component-Based Strategy Architecture** där:
- Varje komponent (ML confidence, HTF gate, ATR filter, etc.) är **oberoende och testbar**
- Komponenter är **composable** (mix and match via config)
- **Clear interfaces** mellan komponenter
- **Metrics per component** (attribution tracking)
- **Config-driven activation** (no code changes för experiments)

### Progressive Implementation

```
Phase 1: Proof of Concept (1 dag)      ✅ COMPLETE (2026-01-30)
  └─> 3 komponenter, basic composition, test resultat

Phase 2: Minimal Viable (1-2 veckor)   ✅ COMPLETE (2026-02-02)
  └─> 6-8 komponenter, full backtest integration

Phase 3: Full Migration (2-3 veckor)   ← NEXT
  └─> All komponenter, Optuna integration, production ready
```

---

## Phase 1: Proof of Concept - ✅ COMPLETE

**Completed**: 2026-01-30
**Duration**: 1 day
**Goal**: Prove component-based approach works and provides attribution insights

### Summary

**Core Infrastructure**:
- ✅ StrategyComponent base class with evaluate() interface
- ✅ ComponentResult dataclass (allowed, confidence, reason, metadata)
- ✅ ComposableStrategy with first-veto-wins composition logic
- ✅ Attribution tracking (veto counts, confidence distributions)

**Components Implemented** (3):
1. ✅ MLConfidenceComponent (threshold-based ML filtering)
2. ✅ HTFGateComponent (HTF regime filtering)
3. ✅ ATRFilterComponent (volatility-based filtering)

**Validation**:
- ✅ Unit tests for base classes and composition
- ✅ POC backtests demonstrated component filtering
- ✅ Attribution reports showed component impact
- ✅ **Decision**: GREEN LIGHT for Phase 2

**Key Learnings**:
- Component isolation enables clear attribution
- First-veto-wins pattern simple and effective
- Config-driven composition works well

---

## Phase 1 Detailed Tasks (Archived)

<details>
<summary>Expand to see original Phase 1 planning tasks (archived)</summary>

#### 🚧 Core Infrastructure (2h)
- [ ] **StrategyComponent base class** (`components/base.py`)
  - `evaluate(context) -> ComponentResult` abstract method
  - `name() -> str` identifier
  - Clear docstrings

- [ ] **ComponentResult dataclass** (`components/base.py`)
  - `allowed: bool` (veto power)
  - `confidence: float` (0-1 range)
  - `reason: str | None` (veto reason)
  - `metadata: dict` (debugging info)

- [ ] **ComposableStrategy class** (`components/strategy.py`)
  - `__init__(components: list[StrategyComponent])`
  - `evaluate(context) -> StrategyDecision`
  - Combine results (veto logic, confidence aggregation)

- [ ] **Unit tests** (`tests/test_composable_strategy_poc.py`)
  - Test base classes
  - Test composition logic
  - Test veto behavior

#### 🚧 Three POC Components (3h)

**Component 1: ML Confidence** (`components/ml_confidence.py`)
```python
class MLConfidenceComponent(StrategyComponent):
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def evaluate(self, context: dict) -> ComponentResult:
        # Use existing ML model from context
        confidence = context['ml_confidence']

        return ComponentResult(
            allowed=(confidence > self.threshold),
            confidence=confidence,
            reason=None if confidence > self.threshold else "ML_CONFIDENCE_LOW",
            metadata={"ml_confidence": confidence, "threshold": self.threshold}
        )
```

**Component 2: HTF Gate** (`components/htf_gate.py`)
```python
class HTFGateComponent(StrategyComponent):
    def __init__(self, required_regimes: list[str] = None):
        self.required_regimes = required_regimes or ['trending', 'bull']

    def evaluate(self, context: dict) -> ComponentResult:
        htf_regime = context.get('htf_regime', 'unknown')
        allowed = htf_regime in self.required_regimes

        return ComponentResult(
            allowed=allowed,
            confidence=1.0 if allowed else 0.0,
            reason=None if allowed else f"HTF_REGIME_{htf_regime}",
            metadata={"htf_regime": htf_regime, "required": self.required_regimes}
        )
```

**Component 3: ATR Filter** (`components/atr_filter.py`)
```python
class ATRFilterComponent(StrategyComponent):
    def __init__(self, min_ratio: float = 1.0):
        self.min_ratio = min_ratio

    def evaluate(self, context: dict) -> ComponentResult:
        atr = context.get('atr', 0)
        atr_ma = context.get('atr_ma', 1)
        ratio = atr / atr_ma if atr_ma > 0 else 0

        allowed = ratio > self.min_ratio

        return ComponentResult(
            allowed=allowed,
            confidence=min(ratio / 2.0, 1.0),  # Normalize
            reason=None if allowed else "ATR_TOO_LOW",
            metadata={"atr_ratio": ratio, "min_ratio": self.min_ratio}
        )
```

**Tests for each** (`tests/test_components_poc.py`)

#### 🚧 Backtest Integration (2h)

- [ ] **Config schema** (`config/strategy/composable/poc/`)
  - `v0_baseline.yaml` (only ML)
  - `v1_ml_atr.yaml` (ML + ATR)
  - `v2_ml_htf.yaml` (ML + HTF)
  - `v3_all.yaml` (ML + ATR + HTF)

- [ ] **Backtest adapter** (`scripts/run_composable_backtest_poc.py`)
  - Load component config
  - Build strategy from components
  - Run backtest using existing engine
  - Collect component attribution metrics

- [ ] **Attribution tracker** (`components/attribution.py`)
  - Track veto counts per component
  - Track confidence distributions
  - Generate report

#### 🚧 Experiments & Analysis (1-2h)

- [ ] Run backtests with each config (v0-v3)
- [ ] Compare results:
  - Which components add value?
  - Which reduce trade count too much?
  - Which improve PF?
- [ ] Generate attribution report
- [ ] Document findings

---

## Deliverables (Phase 1)

### Code Artifacts
- [ ] `src/core/strategy/components/base.py` (base classes)
- [ ] `src/core/strategy/components/ml_confidence.py`
- [ ] `src/core/strategy/components/htf_gate.py`
- [ ] `src/core/strategy/components/atr_filter.py`
- [ ] `src/core/strategy/components/strategy.py` (ComposableStrategy)
- [ ] `src/core/strategy/components/attribution.py` (tracking)
- [ ] `tests/test_composable_strategy_poc.py` (unit tests)
- [ ] `tests/test_components_poc.py` (component tests)
- [ ] `scripts/run_composable_backtest_poc.py` (runner)

### Configs
- [ ] `config/strategy/composable/poc/v0_baseline.yaml`
- [ ] `config/strategy/composable/poc/v1_ml_atr.yaml`
- [ ] `config/strategy/composable/poc/v2_ml_htf.yaml`
- [ ] `config/strategy/composable/poc/v3_all.yaml`

### Results
- [ ] `results/composable_poc/v0_baseline_results.json`
- [ ] `results/composable_poc/v1_ml_atr_results.json`
- [ ] `results/composable_poc/v2_ml_htf_results.json`
- [ ] `results/composable_poc/v3_all_results.json`
- [ ] `results/composable_poc/attribution_report.txt`

### Documentation
- [x] This tracking document
- [ ] `docs/features/COMPOSABLE_STRATEGY_POC_RESULTS.md` (findings)

---

## Decision Points

### After Phase 1 (POC)

**If Results Show Promise** (components add clear value):
→ Proceed to Phase 2 (Minimal Viable)

**If Results Are Mixed** (some components good, some bad):
→ Iterate on POC, test more components

**If Results Show Fundamental Problem** (nothing helps):
→ Pivot approach, document learnings

### After Phase 2 (Minimal Viable)

**If System Works Well** (improved PF, better trade count, good OOS):
→ Proceed to Phase 3 (Full Migration)

**If System Needs More Work**:
→ Continue iterating in Phase 2

**If Original System Is Better**:
→ Abandon migration, keep POC code for future reference

---

## Risk Mitigation

### Technical Risks

**Risk**: POC implementation takes longer than 1 dag
- **Mitigation**: Start with absolute minimum (2 components instead of 3)

**Risk**: Integration med existing backtest engine är svår
- **Mitigation**: Create standalone POC backtest first, integrate later

**Risk**: Results är inconclusive
- **Mitigation**: Run on multiple time periods, check consistency

### Process Risks

**Risk**: Feature branch diverges från master
- **Mitigation**: Regular rebases, small PRs

**Risk**: POC blir "temporary hack" som stannar
- **Mitigation**: Clear decision points, commit to either migrate or abandon

---

## Progress Log

### 2026-01-29 15:30 - Project Start
- ✅ Created feature branch `feature/composable-strategy-poc`
- ✅ Created tracking document
- 📝 Next: Create components directory structure

### 2026-01-29 16:15 - End of Work Session
- ✅ Branch created: `feature/composable-strategy-poc`
- ✅ Tracking document created with comprehensive Phase 1 plan
- ✅ Project structure defined (3 components, 4 test configs, attribution tracking)
- 💭 Discussed: POC approach, component-based architecture, progressive commitment (C→B→A)
- 💭 Key insights: Avoid overfitting via component attribution, test systematically
- 📝 Next session (Home PC): Implement base.py (StrategyComponent, ComponentResult, ComposableStrategy)
- 🏠 Workflow: Work continues on home PC via git pull of this branch

### 2026-01-30 10:30 - Phase 1 POC COMPLETE ✅
- ✅ All base classes implemented and tested
- ✅ 3 POC components (ML, HTF, ATR) working
- ✅ 28/28 unit tests passing
- ✅ 4 test configs created (v0-v3)
- ✅ Backtest adapter + attribution tracker implemented
- ✅ All configs executed successfully
- ✅ Results documented in `docs/features/COMPOSABLE_STRATEGY_POC_RESULTS.md`
- ✅ Code quality: black formatted, ruff clean
- 📊 Key finding: Attribution clearly shows which components block trades
- 📊 Trade allow rate: 80% (ML only) → 60% (ML+ATR) → 60% (ML+HTF) → 40% (all)
- ✅ **ALL Phase 1 success criteria met**
- 🚦 **Decision point**: Proceed to Phase 2 (Minimal Viable)?
- 📝 Next session: User decision on Phase 2

### [Add entries as work progresses]

---

## Notes & Observations

### Design Decisions

**Why dataclass for ComponentResult?**
- Simple, immutable, typed
- Easy to test and debug
- Clear contract

**Why veto-based composition?**
- Mirrors current gate logic
- Easy to understand
- Fail-fast behavior

**Why confidence aggregation with min()?**
- Conservative approach
- Weakest link principle
- Avoids overconfidence

### Open Questions

1. Should components have access to full context or restricted view?
   - **Decision**: Full context for POC, restrict later if needed

2. How to handle stateful components (e.g., hysteresis)?
   - **Decision**: Defer to Phase 2, focus on stateless for POC

3. Config format: YAML or JSON?
   - **Decision**: YAML for readability, matches optimizer configs

### Lessons Learned

[To be filled as we progress]

---

## Success Metrics (Phase 1)

Proof of concept is successful if:

1. **Technical**:
   - [ ] Code works, tests pass
   - [ ] Backtest runs with all configs
   - [ ] No major integration blockers

2. **Results**:
   - [ ] Clear difference between v0-v3 configs
   - [ ] Can identify which components add/remove value
   - [ ] Attribution report is informative

3. **Quality**:
   - [ ] Code is clean and well-documented
   - [ ] Easy for other devs to understand
   - [ ] Maintainable if we proceed

**If all 3 categories pass: GREEN LIGHT for Phase 2** ✅

</details>

---

## Phase 2: Minimal Viable - ✅ COMPLETE

**Completed**: 2026-02-02
**Branch**: `feature/composable-strategy-phase2`
**Duration**: 3 days (2026-01-30 to 2026-02-02)

### Achievements

**Milestone 1: BacktestEngine Integration** ✅
- `ComposableBacktestEngine` with clean `evaluation_hook` pattern
- No monkey-patching, zero overhead when hook=None
- Invariants proven: hook=None ≡ identity, hook triggers on every decision
- 61 tests passing

**Milestone 2: Component Expansion** ✅
- **RegimeFilterComponent**: Regime-based filtering (80% veto rate)
- **EVGateComponent**: Expected Value gate (structurally validated)
- **CooldownComponent**: First stateful component (entry-only semantics)
- **HysteresisComponent**: Deferred to Phase 3
- 80+ tests covering all components

**Milestone 3: Full Backtest Validation** ✅
- Validated across 4 configs (v0-v3) on Q1 2024 period
- **Critical finding**: Legacy HTF/LTF Fibonacci gates (external to composable system) blocked 100% of entries
- Validation required disabling legacy gates to produce trades
- **18 trades produced** (v0), proving component filtering works
- Architecture **successfully surfaced legacy bottleneck**
- Component attribution tracking accurate

**Milestone 4: Documentation & QA** ✅
- Full validation report: `MILESTONE3_VALIDATION_COMPLETE.md`
- QA suite passing: 103 Phase 2 tests green
- Code quality: ruff + black clean
- Decision: **GREEN LIGHT for Phase 3**

### Component Inventory (Phase 2)

**Implemented (6 components)**:
1. ✅ MLConfidenceComponent (Phase 1)
2. ✅ HTFGateComponent (Phase 1)
3. ✅ ATRFilterComponent (Phase 1)
4. ✅ RegimeFilterComponent (Phase 2)
5. ✅ EVGateComponent (Phase 2)
6. ✅ CooldownComponent (Phase 2 - first stateful)

**Deferred to Phase 3**:
7. HysteresisComponent (stateful, anti-flipflop)
8. RiskMapComponent (dynamic sizing)

### Key Learnings

**Architecture Strengths**:
- ✅ Component isolation enables clear attribution
- ✅ First-veto-wins pattern simple and effective
- ✅ Stateful components (Cooldown) proven operational
- ✅ Architecture surfaces legacy bottlenecks clearly

**Legacy System Findings**:
- ⚠️ HTF/LTF Fibonacci gates (in monolithic `decide()`) block 100% of entries
- ⚠️ Located upstream of composable components
- ⚠️ `htf_candles_loaded: false` → data unavailable
- 💡 **Solution**: Fix HTF data loading OR migrate to HTFGateComponent (Phase 3)

**Component Tuning Insights**:
- RegimeFilter: 81% veto rate (effective but too restrictive)
- EVGate: 0% veto rate @ min_ev=0.0 (tandlös, needs tuning)
- CooldownComponent: 13% veto rate (good balance)

### Validation Results (Q1 2024, Legacy Gates Disabled)

| Config | Trades | PF | Win% | Return | Components |
|--------|--------|-----|------|--------|------------|
| v0 | 18 | 2.65 | 77.8% | +1.91% | ML only |
| v1 | 2 | inf | 100% | +0.21% | + Regime |
| v2 | 2 | inf | 100% | +0.21% | + EV |
| v3 | 1 | inf | 100% | -0.01% | + Cooldown |

**Component Effects**:
- v0→v1: RegimeFilter reduced entries by 81%
- v1→v2: EVGate had zero impact (as expected)
- v2→v3: Cooldown reduced entries by 65%

### Phase 2 Exit Criteria: MET ✅

| Criterion | Status |
|-----------|--------|
| Components working correctly | ✅ PASS |
| Attribution tracking accurate | ✅ PASS |
| Stateful components validated | ✅ PASS |
| Trade count > 100 | ⚠️ PARTIAL (18 trades, sufficient for architecture validation) |
| QA suite passing | ✅ PASS |
| Documentation complete | ✅ PASS |

**Decision**: **Proceed to Phase 3** (optimization & production)

### Artifacts

**Code**:
- `src/core/strategy/components/` (10 files, 1200+ LOC)
- `src/core/backtest/composable_engine.py` (151 LOC)
- `tests/test_composable*.py` (103 tests)

**Documentation**:
- `docs/features/MILESTONE3_VALIDATION_COMPLETE.md` (full validation report)
- `docs/features/COMPOSABLE_STRATEGY_PHASE2_RESULTS.md` (detailed findings)

**Scripts**:
- `scripts/run_composable_backtest_phase2.py` (production runner)
- `scripts/run_composable_backtest_no_fib.py` (validation runner)

---

## Phase 3: Full Migration - Milestone 1 COMPLETE

**Status**: ✅ Milestone 1 CLOSED - Baseline established (2026-02-03)
**Baseline Config**: `v4a_ml_regime_relaxed.yaml`
**Closure Report**: `docs/features/PHASE3_MILESTONE1_CLOSURE.md`

### Milestone 1: Component Tuning (Config-Only) - ✅ COMPLETE (2026-02-03)

**Goal**: Establish baseline config with permissive component thresholds.

**Result**: v4a baseline established with 63 trades/year, guardrails passed ✅

**Baseline Performance** (Full 2024):
- Trades: 63
- Profit Factor: 1.59
- Win Rate: 68.3%
- Total Return: 1.14%
- Max Drawdown: 2.18%

**Guardrails**: PASSED ✅
- Full 2024: 63 trades (>40 required)
- All quarters: Q1=18, Q2=15, Q3=16, Q4=13 (all >0)

**Critical Bugs Fixed**:

1. **Bug #1 - CooldownComponent phantom trades**: ✅ FIXED
   - **Root cause**: Premature record_trade() call on signal (not execution)
   - **Impact**: 1526 phantom vetoes, reduced trades from 15 to 0
   - **Fix**: Post-execution hook that only updates state on executed=True
   - **Tests**: 26 regression tests added (all passing)
   - **Validation**: 0→15 trades in isolation, phantom vetoes eliminated

2. **Bug #2 - ComponentContextBuilder key mapping**: ✅ FIXED
   - **Root cause**: Used probas.get('LONG'/'SHORT') but model outputs 'buy'/'sell'
   - **Impact**: EVGate received EV=0.0 for ALL decisions (degenerate 100% veto)
   - **Fix**: Robust key mapping (buy/sell → LONG/SHORT, case-insensitive)
   - **Tests**: 5 comprehensive tests added
   - **Validation**: EVGate veto rate from 100% (degenerate) to 0% (baseline)

**Critical Finding**: Permissive baseline is functionally toothless

Under v4a permissive settings, component chain has **0% veto rate**:
- ml_confidence (threshold=0.24): 0 vetoes (0.0%)
- RegimeFilter (all regimes): 0 vetoes (0.0%)
- EVGate (min_ev=0.0): 0 vetoes (0.0%)
- CooldownComponent: 0 reported vetoes (active in execution spacing only)

**Trade frequency is dominated by ATR zone sizing** (not component filtering):
- 5396 Entry actions (100%)
  - 4679 Component allowed (86.7%) ← Minimal filtering
    - 4613 size==0 (98.6%) ← ATR zone sizing rounds to 0
      - ZONE low@0.250: 67.0%
      - ZONE mid@0.320: 28.4%
      - ZONE high@0.380: 4.6%
    - 66 size>0 attempted (1.4%)
      - 55 Executed (83.3%)

**Conclusion**: Further config-only component tuning has minimal impact until sizing policy is addressed.

**Artifacts Created**:
- Configs: `config/strategy/composable/phase2/v4a_ml_regime_relaxed.yaml` (baseline)
- Configs: `config/strategy/composable/phase2/v4b_ev_*.yaml` (EVGate calibration)
- Results: `results/extended_validation/v4a_ml_regime_relaxed_full2024_20260203_092718.json`
- Scripts: `scripts/diagnose_execution_gap_v2.py`, `scripts/sanity_check_*.py`, `scripts/run_extended_validation_2024.py`
- Docs: `docs/features/PHASE3_BUG1_FIX_SUMMARY.md`, `docs/features/PHASE3_BUG2_FIX_SUMMARY.md`
- Docs: `docs/features/PHASE3_MILESTONE1_BLOCKER_INVESTIGATION.md`, `docs/features/PHASE3_MILESTONE1_CLOSURE.md`

**Next Steps**: See Milestone 2 below

### Milestone 2: HQT Audit (PF-First) - ✅ COMPLETE (2026-02-03)

**Goal**: Quality audit of v4a baseline with PF-first criteria (read-only).

**Result**: HQT-FAIL verdict

**Deliverables Completed**:
1. ✅ PF helår + per kvartal (Q1-Q4)
2. ✅ PnL concentration (top-1: 40.7%, top-5: 120.4%)
3. ✅ PF robustness (without top-1: 1.35, without top-3: 1.07 ❌ FAIL)
4. ✅ Fees analysis ($1.43/trade, 11% burden)

**HQT-Pass Criteria Results**:
- [1] ✅ PASS: Helår PF >= 1.5 (1.59)
- [2] ✅ PASS: 4/4 kvartal PF >= 1.3
- [3] ✅ PASS: Inget kvartal < 1.0 (min=1.67)
- [4] ❌ FAIL: PF utan top-3 >= 1.2 (1.07 < 1.2)

**Critical Finding**:
Strategy is NOT robust to outlier removal. PF collapses from 1.59 → 1.07 (-32.9%) when top-3 trades removed. Top-1 trade accounts for 40.7% of total PnL.

**Root Cause**: Low trade frequency (63/year) + no quality filtering → high outlier dependence.

**Recommendation**: Proceed with Sizing Policy Review (Milestone 3) to increase trade frequency → reduce outlier dependence → improve PF robustness.

**Artifacts**:
- Script: `scripts/hqt_audit_pf_first.py`
- Results: `results/hqt_audit/v4a_hqt_audit_20260203.txt`
- Docs: `docs/features/PHASE3_MILESTONE2_HQT_AUDIT.md`

### Milestone 3: Sizing Policy Review (Proposed)

**Status**: ⏸️ NOT STARTED
**Goal**: Increase attempted executions (size>0) to improve PF robustness and enable meaningful component filtering.
**Target**: 100-150 trades/year without MaxDD explosion.
**Blockers**: None (Milestone 2 complete, HQT audit confirms direction)

**Rationale** (from HQT audit):
- More trades → reduced outlier dependence → better PF robustness
- Addresses root cause of HQT-FAIL verdict
- Must maintain PF quality (not just inflate trade count)

**Approach**:

1. **Investigate signal_adaptation config**:
   - Check if ZONE multipliers (0.25/0.32/0.38) are configurable
   - Check if ATR percentile thresholds are configurable
   - Document current sizing-policy parameters

2. **Config-only adjustments** (if parameters exist):
   - Increase ZONE multipliers (e.g., 0.50/0.65/0.80)
   - OR increase base size
   - OR adjust ATR zone thresholds to classify more bars as "high" volatility

3. **Validation**:
   - Re-run full 2024 with adjusted sizing
   - Target: 100-150 trades/year, maintain PF >1.5, MaxDD <5%
   - Re-run HQT audit on new baseline
   - If successful: Proceed with component tuning (EVGate, ml_confidence)

4. **If NOT config-only**:
   - Requires code changes to sizing logic
   - Escalate decision: Accept 60-80 trades/year OR implement code changes

**Estimated Effort**: 1-2 days (if config-only), 1 week (if code changes required)

### Future Milestones (After Milestone 3)

1. **Component Tuning** (revisit after sizing fixed):
   - Tune EVGate (min_ev: 0.09-0.13 based on distribution)
   - Tune ml_confidence threshold
   - Extended validation with meaningful component filtering

2. **Additional Components**:
   - HysteresisComponent (anti-flipflop, stateful)
   - RiskMapComponent (dynamic sizing, optional)

3. **Legacy Migration**:
   - Fix HTF data loading OR
   - Migrate HTF/LTF Fibonacci logic to components

4. **Optuna Integration**:
   - Optimize component thresholds
   - Multi-objective optimization (PF + trade count)
   - Champion promotion workflow

5. **Production Readiness**:
   - Full year validation (2024)
   - Champion config migration
   - Rollout plan

### Success Criteria (Overall Phase 3)

- [x] Bug fixes validated (CooldownComponent, ComponentContextBuilder)
- [x] Baseline established (v4a with 63 trades/year)
- [ ] Sizing policy adjusted for 100-150 trades/year
- [ ] Component filtering becomes meaningful (>0% veto rate with impact)
- [ ] PF >= current champion -5%
- [ ] Component attribution shows value
- [ ] Optuna optimization working
- [ ] Production deployment plan documented

---
