# Composable Strategy Architecture - Project Tracking

**Branch**: `feature/composable-strategy-poc`
**Started**: 2026-01-29
**Status**: 🚧 Phase 1 - Proof of Concept (In Progress)
**Owner**: Claude Code + User

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
Phase 1: Proof of Concept (1 dag)      ← WE ARE HERE
  └─> 3 komponenter, basic composition, test resultat

Phase 2: Minimal Viable (1-2 veckor)   ← IF Phase 1 successful
  └─> 6-8 komponenter, full backtest integration

Phase 3: Full Migration (2-3 veckor)   ← IF Phase 2 validated
  └─> All komponenter, Optuna integration, production ready
```

---

## Phase 1: Proof of Concept (Current)

**Goal**: Bevisa att component-based approach fungerar och ger värdefulla insights

**Timeline**: 1 dag (6-8 timmar arbete)

**Success Criteria**:
- [ ] 3 komponenter implementerade och testade
- [ ] Komponenter går att kombinera via config
- [ ] Backtest körs med olika kombinationer
- [ ] Results visar vilket som ger värde
- [ ] Koden är ren och maintainable

### Tasks

#### ✅ Setup (30 min)
- [x] Skapa feature branch: `feature/composable-strategy-poc`
- [x] Skapa tracking dokument: `docs/features/COMPOSABLE_STRATEGY_PROJECT.md`
- [ ] Skapa working directory: `src/core/strategy/components/` (POC code här)

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

---

## References

- Original discussion: Session 2026-01-29
- Related docs: `CLAUDE.md`, `AGENTS.md`
- Current strategy: `src/core/strategy/decision.py`
- Current results: `config/strategy/champions/tBTCUSD_1h.json`
