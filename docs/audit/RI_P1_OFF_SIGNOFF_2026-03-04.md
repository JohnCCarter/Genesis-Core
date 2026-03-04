# RI P1 OFF Signoff — Implementation Report

Datum: 2026-03-04
Branch: `feature/regime-intelligence-p1-signoff`
Mode: `RESEARCH` (source=branch mapping `feature/*`)
Risk: `MED`
Required path: `Full` (non-trivial)
Base SHA: `02b660ab7f0f8c79e3f44cc821bb864b7122f0e3`

## Scope

### Scope IN

- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`
- `.github/copilot-instructions.md`
- `scripts/archive/2026-02/analysis/run_backtest.py` (deleted)
- `scripts/run/run_backtest.py`
- `tools/compare_backtest_results.py`
- `tests/test_compare_backtest_results.py`
- Formattering (black-only):
  - `scripts/extract/extract_backtest_provenance.py`
  - `scripts/optimize/optimizer.py`
  - `scripts/preflight/preflight_optuna_check.py`
  - `scripts/promote/promote_v5a_to_champion.py`
  - `scripts/run/paper_trading_runner.py`
  - `scripts/run/run_skill.py`
  - `scripts/validate/validate_optimizer_config.py`
  - `scripts/validate/validate_registry.py`

### Scope OUT

- Inga ändringar i `config/strategy/champions/`
- Ingen ändring i freeze-guard workflows
- Ingen ändring i runtime default-semantik för live/paper-flöden

## Skill Usage

- Skills referenced:
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skills executed:
  - `ri_off_parity_artifact_check@1.0.0` via `dev` manifest
  - `run_id=c8c3b77cd2c1`
  - Audit log: `logs/skill_runs.jsonl` (Triggered/Verified/Result=PASS)
- Skill proposals: none
- Skill updates: none

## Gate matrix

Körningar och utfall:

- `black --check .` => PASS (`black_exit=0`)
- `ruff check .` => PASS (`ruff_exit=0`)
- Smoke selector => PASS (`smoke_exit=0`)
- Determinism replay selector => PASS (`determinism_exit=0`)
- Feature cache invariance selector => PASS (`feature_cache_exit=0`)
- Pipeline invariant selector => PASS (`pipeline_invariant_exit=0`)

Källa: `tmp/strict_gates_rerun_20260304c.log`

Ytterligare RI-fokuserade verifieringar i sessionen:

- `tests/test_compare_backtest_results.py` => PASS
- `tests/test_run_backtest_decision_rows.py` => PASS

## Artifacts

- RI parity artifact: `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`
  - `parity_verdict=PASS`
  - mismatch counts: `action=0`, `reason=0`, `size=0`, `added=0`, `missing=0`
  - `git_sha=02b660ab7f0f8c79e3f44cc821bb864b7122f0e3`
  - `window_spec_id=ri_p1_off_parity_v1`

## Baseline provenance wording (korrigerad)

RI P1 OFF parity-artifactet verifierar rad-paritet mot baseline som refereras via `baseline_artifact_ref`. Artifactet innehåller `git_sha`, `run_id`, fönster/symbol/timeframe och mismatch-räknare; detta är paritetsbevis, inte en fullständig provenansattest av baseline-genereringen.

## Behavior-change kandidat (tooling-kontrakt)

- `tools/compare_backtest_results.py` behandlar `size=None` vs `size=None` som match i RI parity-radjämförelse.
- Klassning: behavior change candidate i comparator-tooling (inte runtime/live-exekvering).
- Default runtime-beteende i strategi/backtest-pipeline lämnas oförändrat.

## Residual risker

- Låg risk för regressions i runtime eftersom ändringen är koncentrerad till parity-verktyg + tester och gated decision-row export.
- Medel risk för feltolkning om comparator-kontraktsändringen inte dokumenteras i PR-beskrivning.

## READY_FOR_REVIEW evidenscheck

- [x] Mode/risk/path dokumenterat
- [x] Scope IN/OUT dokumenterat
- [x] Exakta gates + outcomes dokumenterade
- [x] Relevanta selectors/artifacts bifogade
- [x] Skill usage dokumenterad med run_id
