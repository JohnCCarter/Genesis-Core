## COMMAND PACKET

- **Mode:** `STRICT` — source: branch mapping (`master`) via `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches `src/core/backtest/**` in the champion execution path, even though the slice is shadow-only and must preserve decision parity
- **Required Path:** `Full`
- **Objective:** Implement an opt-in champion shadow integration that runs `DeterministicResearchOrchestrator` during backtest execution against the existing `tBTCUSD_3h` champion path, emits deterministic intelligence shadow artifacts, and guarantees no change to action, size, reasons, trades, or exit behavior.
- **Candidate:** `master` working tree, non-default shadow-only experiment slice
- **Base SHA:** `70f6ef1435e9005fdbe171f954b8886f9bc63528`

### Scope

- **Scope IN:**
  - `docs/audit/research_system/context_map_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
  - `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
  - `docs/features/feature-champion-shadow-intelligence-1.md`
  - `scripts/run/run_backtest.py`
  - `src/core/backtest/intelligence_shadow.py`
  - `tests/backtest/test_run_backtest_intelligence_shadow.py`
  - `tests/integration/test_backtest_champion_intelligence_shadow.py`
- **Scope OUT:**
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `src/core/strategy/**`
  - `src/core/intelligence/**`
  - `src/core/research_orchestrator/**`
  - `src/core/research_ledger/**`
  - default/promotion/cutover claims
  - live execution, scheduler logic, database logic, API changes
- **Expected changed files:** `6-7`
- **Max files touched:** `7`

### Gates required

- `python -m black --check scripts/run/run_backtest.py src/core/backtest tests/backtest tests/integration docs/audit/research_system docs/features`
- `python -m ruff check scripts/run/run_backtest.py src/core/backtest tests/backtest tests/integration`
- `python -m pytest tests/backtest/test_run_backtest_intelligence_shadow.py -q`
- `python -m pytest tests/integration/test_backtest_champion_intelligence_shadow.py -q`
- `python -m pytest tests/research_orchestrator -q`
- `python -m pytest tests/intelligence -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- `python -m pytest tests/utils/test_feature_cache.py -q`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py -q`
- Required focused evidence within/alongside test run:
  - control-vs-shadow parity proof on `action`, `size`, `reasons`, trade count, and exit code
  - shadow artifact summary count determinism
  - persisted event ids / ledger entity ids determinism
  - backtest determinism replay with shadow path enabled

### Stop Conditions

- Any need to mutate `result`, `meta`, `configs`, or `state` in-place inside the shadow hook
- Any need to modify `config/runtime.json`, champion files, strategy decision logic, or shared intelligence/orchestrator/ledger contracts
- Any implicit activation path that enables shadow mode without an explicit CLI flag/path
- Any write outside approved roots:
  - `results/intelligence_shadow/<run_id>/...` for summary artifacts
  - `artifacts/intelligence_shadow/<run_id>/research_ledger/...` for shadow ledger storage
- Any shadow failure that would silently alter or skip normal trade execution without an explicit and tested failure policy
- Any inability to prove identical decision/trade outputs between control and shadow-enabled runs

### Output required

- **Implementation Report**
- **PR evidence template**
- **Shadow summary artifact:** machine-readable JSON under `results/intelligence_shadow/<run_id>/shadow_summary.json`
- **Ledger artifact root:** deterministic shadow ledger storage under `artifacts/intelligence_shadow/<run_id>/research_ledger/`
- **Boundary note:** derived approved parameter set is advisory-only, fingerprint-based, and must not be interpreted as champion selection or promotion evidence
