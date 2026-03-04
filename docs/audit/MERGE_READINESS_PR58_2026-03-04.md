# Merge Readiness — PR #58

Datum: 2026-03-04
PR: https://github.com/JohnCCarter/Genesis-Core/pull/58
Branch: `feature/regime-intelligence-p1-signoff`
Base: `master`
Head commit: `a174f60df8badff9c499920e4a6233426614eb3b`
Ahead of `master`: `1` commit

## Executive summary

PR #58 är merge-ready utifrån tillgänglig evidens:

- Opus slutstatus: **APPROVED**
- Färsk gate-replay: alla exit-koder `0` i `tmp/strict_gates_rerun_20260304c.log`
- Skill-evidens: `ri_off_parity_artifact_check` PASS (`run_id=c8c3b77cd2c1`)
- RI parity-artifact: PASS (`results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`)

## Riskklassning inför merge

- Total risk: **MED**
- Runtime default drift: **Low** (decision-row capture är opt-in)
- Tooling kontraktsjustering: **Med** (`None/None` size-match i comparator)
- Freeze-zoner: **No touch** (`config/strategy/champions/` oförändrad)

## Ändringsyta mot master (name-status)

- `M` `.github/agents/Codex53.agent.md`
- `M` `.github/agents/Opus46.agent.md`
- `M` `.github/copilot-instructions.md`
- `A` `docs/audit/PR_RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `A` `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `D` `scripts/archive/2026-02/analysis/run_backtest.py`
- `M` `scripts/extract/extract_backtest_provenance.py`
- `M` `scripts/optimize/optimizer.py`
- `M` `scripts/preflight/preflight_optuna_check.py`
- `M` `scripts/promote/promote_v5a_to_champion.py`
- `M` `scripts/run/paper_trading_runner.py`
- `M` `scripts/run/run_backtest.py`
- `M` `scripts/run/run_skill.py`
- `M` `scripts/validate/validate_optimizer_config.py`
- `M` `scripts/validate/validate_registry.py`
- `M` `tests/test_compare_backtest_results.py`
- `A` `tests/test_run_backtest_decision_rows.py`
- `M` `tools/compare_backtest_results.py`

## Rekommenderad merge-strategi

Eftersom branchen är **1 commit ahead** rekommenderas:

1. **Squash and merge** (ren historik och enkel revert), eller
2. **Rebase and merge** (om man vill behålla commit-meddelandet exakt)

Båda är acceptabla. Praktiskt default: **Squash and merge**.

## Rollback-plan

Om regression upptäcks efter merge:

1. Revertera merge-commit i `master` (eller revert av commit som introducerats via squash).
2. Verifiera att följande selectors återgår till grönt:
   - smoke
   - determinism replay
   - feature cache invariance
   - pipeline invariant
   - RI comparator tests
   - decision row tests
3. Bekräfta att PR #58 artifacts fortfarande speglar pre-rollback state i audit-loggar.

## Post-merge kontrollpunkter

- Bekräfta att `scripts/run/run_backtest.py` fungerar i defaultläge utan `--decision-rows-out`.
- Bekräfta att comparator-kontraktet (`None/None` size) är tydligt i release-notes/PR-tråd.
- Säkerställ att docs-evidens länkar förblir tillgängliga:
  - `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`
  - `docs/audit/PR_RI_P1_OFF_SIGNOFF_2026-03-04.md`
  - `tmp/strict_gates_rerun_20260304c.log`
  - `logs/skill_runs.jsonl` (run_id `c8c3b77cd2c1`)

## Slutsats

**READY_TO_MERGE** med ovanstående rollback-plan och post-merge kontroller.
