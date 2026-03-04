# PR Title

`tooling: RI P1 OFF parity signoff, decision-row capture, and comparator None/None parity fix`

# PR Description

## Summary

Detta PR-paket färdigställer RI P1 OFF signoff med komplett governance-evidens och no-drift-default i runtime.

Huvudpunkter:

- Canonicaliserar `run_backtest` till `scripts/run/run_backtest.py` (archive-kopian borttagen).
- Lägger till beslutrads-capture (`--decision-rows-out`, `--decision-rows-format`) med passiv hook-komposition.
- Justerar RI-parity comparator så `size=None` vs `size=None` räknas som match.
- Lägger till riktade tester för comparatorn och decision-row-capture.
- Dokumenterar full signoff med skill usage, gates och artifacts.

## Mode / Risk / Path

- Mode: `RESEARCH` (branch mapping `feature/*`)
- Risk: `MED`
- Required path: `Full` (non-trivial)

## Scope IN

- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`
- `.github/copilot-instructions.md`
- `scripts/archive/2026-02/analysis/run_backtest.py` (deleted)
- `scripts/run/run_backtest.py`
- `tools/compare_backtest_results.py`
- `tests/test_compare_backtest_results.py`
- `tests/test_run_backtest_decision_rows.py` (new)
- Black-only formatting in:
  - `scripts/extract/extract_backtest_provenance.py`
  - `scripts/optimize/optimizer.py`
  - `scripts/preflight/preflight_optuna_check.py`
  - `scripts/promote/promote_v5a_to_champion.py`
  - `scripts/run/paper_trading_runner.py`
  - `scripts/run/run_skill.py`
  - `scripts/validate/validate_optimizer_config.py`
  - `scripts/validate/validate_registry.py`

## Scope OUT

- Inga ändringar i `config/strategy/champions/`
- Ingen ändring i freeze-guard workflows
- Ingen ändring i runtime default-semantik för live/paper

## Behavior sensitivity

- **Behavior change candidate (tooling-kontrakt):**
  - `tools/compare_backtest_results.py`: `size=None` vs `size=None` räknas nu som match i RI parity-radjämförelse.
- Runtime/live-defaults är oförändrade.

## Skill Usage

- Skills referenced:
  - `.github/skills/ri_off_parity_artifact_check.json`
- Skills executed:
  - `ri_off_parity_artifact_check@1.0.0` via `dev` manifest
  - `run_id=c8c3b77cd2c1`
  - Log: `logs/skill_runs.jsonl` (Triggered/Verified/Result=PASS)
- Skill proposals: none
- Skill updates: none

## Evidence

- Base SHA (head underlag): `02b660ab7f0f8c79e3f44cc821bb864b7122f0e3`
- Signoff report: `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`
- RI parity artifact:
  - `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`
  - `parity_verdict=PASS`, mismatch counts alla `0`

## Gates executed

Källa (färsk replay): `tmp/strict_gates_rerun_20260304c.log`

- `black --check .` => `black_exit=0`
- `ruff check .` => `ruff_exit=0`
- smoke selector => `smoke_exit=0`
- determinism replay => `determinism_exit=0`
- feature cache invariance => `feature_cache_exit=0`
- pipeline invariant => `pipeline_invariant_exit=0`
- RI comparator tests => `compare_ri_exit=0`
- decision row tests => `decision_rows_exit=0`

## Baseline provenance wording (locked)

RI P1 OFF parity-artifactet verifierar rad-paritet mot baseline som refereras via `baseline_artifact_ref`. Artifactet innehåller `git_sha`, `run_id`, fönster/symbol/timeframe och mismatch-räknare; detta är paritetsbevis, inte en fullständig provenansattest av baseline-genereringen.

## READY_FOR_REVIEW checklist

- [x] Mode/risk/path documented
- [x] Scope IN/OUT documented
- [x] Exact gates + outcomes documented
- [x] Relevant selectors/artifacts attached
- [x] Skill Usage completed
- [x] Behavior-sensitive area explicitly called out

## Opus status

- Post-audit: `APPROVED`
- Final readiness check after fresh replay: `APPROVED`
