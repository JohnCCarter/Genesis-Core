# current_atr 1435 default-off trial packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / research / execution-only / no-runtime-edits`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice performs a non-trivial execution-only research run with artifact generation and containment requirements, but it authorizes no `src/**`, `tests/**`, `config/**`, or `tmp/**` edits.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** Run a bounded execution-only default-off trial for `current_atr >= 1435.209570` on the already implemented research seam, using current code as-is and writing only the approved trial artifacts.
- **Candidate:** `current_atr 1435 default-off execution-only trial`
- **Base SHA:** `e578898448711ad5b2aeca1d2ad3a3bef7342e54`

### Scope

- **Scope IN:**
  - `docs/decisions/current_atr_1435_default_off_trial_packet_2026-04-16.md`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16/manifest.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16/trial_summary.json`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16/closeout.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**` edits
  - any runtime default / config-authority semantics / API contract changes
  - any output outside `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16/`
- **Expected changed files:**
  - `docs/decisions/current_atr_1435_default_off_trial_packet_2026-04-16.md`
  - approved trial artifacts only in the output root above
- **Max files touched:** `4 tracked-or-approved paths`

### Skill Usage

- **Repo-local skill specs to apply:**
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/python_engineering.json`
- **Why these skills apply:**
  - `genesis_backtest_verify` is the relevant bounded verification anchor for deterministic backtest/result comparison discipline.
  - `python_engineering` applies because the execution uses workspace Python directly to orchestrate a read-only helper-driven trial and write exactly three approved artifacts.
- **Skill coverage boundary:**
  - This slice uses those skills as governance/verification anchors only.
  - It does not claim broader process coverage beyond the explicit gates and outputs listed below.

## What this packet does and does not do

This slice runs an execution-only research trial on a seam that already exists in current code.

It does:

- execute existing code on current HEAD
- carry forward already existing implementation/test evidence
- write only the approved artifacts in the approved output root

It does **not**:

- edit `src/**`
- edit `tests/**`
- edit `config/**`
- edit `tmp/**`
- re-authorize runtime implementation work
- promote defaults
- claim runtime readiness

If any code/config/test/tmp edit becomes necessary, this slice must stop immediately and reopen as a separate implementation packet.

## Existing implementation and proof surfaces carried forward

### Existing implementation surface

- `src/core/strategy/decision_sizing.py`
  - `_apply_current_atr_selective_high_vol_multiplier`
  - application inside the existing high-vol sizing path
- `src/core/config/schema.py`
  - `ResearchCurrentATRHighVolMultiplierOverrideConfig`
  - mounting under `multi_timeframe.research_current_atr_high_vol_multiplier_override`
- `src/core/config/authority.py`
  - whitelist support for `enabled`, `current_atr_threshold`, and `high_vol_multiplier_override`

### Existing bounded parity proof

- `tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_absent_matches_explicit_disabled`
- `tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_replaces_high_vol_multiplier`
- `tests/governance/test_config_schema_backcompat.py::test_validate_current_atr_selective_override_absent_matches_explicit_false_leaf`

These surfaces are carried forward as existing evidence only.
They are not re-verified by this packet itself; they must instead be preserved and, where listed below, re-run as explicit gates for this slice.

## Locked read-only inputs

The execution may read only these pinned repo-relative inputs for candidate/tradeoff context:

- helper execution surface (read-only, no edits allowed):
  - `tmp/current_atr_1435_policy_validation_20260416.py`
- candidate `1435` config artifact:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/candidate_1435_cfg.json`
- candidate `900` config artifact:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- baseline `0.90` config artifact:
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`

The execution may also cite, but not modify, the prior evidence chain:

- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/replay_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/replay_summary.json`
- `docs/decisions/current_atr_900_vs_1435_policy_handoff_2026-04-16.md`

## Execution-basis discipline

This slice must record the mixed execution-basis chain explicitly:

- `900` dedicated validation and `900` environment-profile evidence were generated on `8e23ddb45d08784e8a8a340f83334f5842505e0e`
- `1435` policy-validation evidence was generated on `2ee708c9a85a1f3b14dd597b8e2155c5847e91c5`
- this execution-only trial is expected to run on `e578898448711ad5b2aeca1d2ad3a3bef7342e54`

If actual HEAD at execution time differs from `e578898448711ad5b2aeca1d2ad3a3bef7342e54`, the trial must describe itself as a **rebased execution basis** rather than as an unchanged continuation of this packet.

## Trial shape

The execution-only trial must:

- use canonical env flags
- use the existing `1435` seam exactly as already implemented
- treat `900` as a cited tradeoff/reference candidate via the pinned existing artifacts only; this slice must not launch a fresh `900` replay, backtest, or artifact write
- keep default behavior unchanged when the trial seam is absent
- fail closed if any edit would be required to make the run work

The trial may use workspace Python inline execution to import existing helper functions from `tmp/current_atr_1435_policy_validation_20260416.py`, but it may not edit that file.

### Canonical env pins

The bounded execution must run with exactly these env values:

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `SYMBOL_MODE=realistic`

### Exact bounded execution command

The approved execution command for this slice is the following PowerShell + inline Python invocation, run from the repository root:

```powershell
$env:GENESIS_RANDOM_SEED = '42'
$env:GENESIS_FAST_WINDOW = '1'
$env:GENESIS_PRECOMPUTE_FEATURES = '1'
$env:GENESIS_MODE_EXPLICIT = '1'
$env:GENESIS_FAST_HASH = '0'
$env:SYMBOL_MODE = 'realistic'
$trialCode = @'
from __future__ import annotations
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(r"C:/Users/fa06662/Projects/Genesis-Core")
PACKET = ROOT / "docs/decisions/current_atr_1435_default_off_trial_packet_2026-04-16.md"
HELPER = ROOT / "tmp/current_atr_1435_policy_validation_20260416.py"
OUTPUT_DIR = ROOT / "results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16"
MANIFEST_OUT = OUTPUT_DIR / "manifest.json"
SUMMARY_OUT = OUTPUT_DIR / "trial_summary.json"
CLOSEOUT_OUT = OUTPUT_DIR / "closeout.md"
CANDIDATE_1435 = ROOT / "results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_policy_validation_2026-04-16/candidate_1435_cfg.json"
CANDIDATE_900 = ROOT / "results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json"
BASELINE_090 = ROOT / "results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json"
BASE_SHA = "e578898448711ad5b2aeca1d2ad3a3bef7342e54"  # pragma: allowlist secret
EXPECTED_ENV = {
  "GENESIS_RANDOM_SEED": "42",
  "GENESIS_FAST_WINDOW": "1",
  "GENESIS_PRECOMPUTE_FEATURES": "1",
  "GENESIS_MODE_EXPLICIT": "1",
  "GENESIS_FAST_HASH": "0",
  "SYMBOL_MODE": "realistic",
}

if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
  raise SystemExit(f"Output dir is not empty: {OUTPUT_DIR}")
for key, expected in EXPECTED_ENV.items():
  actual = os.environ.get(key)
  if actual != expected:
    raise SystemExit(f"Canonical env mismatch for {key}: expected {expected}, got {actual}")

spec = importlib.util.spec_from_file_location("current_atr_1435_trial_helpers", HELPER)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

git_sha = module._resolve_git_sha()
execution_basis_note = None
if git_sha != BASE_SHA:
  execution_basis_note = (
    f"This trial is a rebased execution basis from {BASE_SHA} to {git_sha}."
  )

approved_files = [MANIFEST_OUT, SUMMARY_OUT, CLOSEOUT_OUT]
allowed_scope_paths = {
  module._normalize_rel_path(module._relative_path(PACKET)),
  *{module._normalize_rel_path(module._relative_path(path)) for path in approved_files},
}
pre_git_status_short = module._get_git_status_short()
module._validate_clean_preflight(
  status_lines=pre_git_status_short,
  allowed_scope_paths=allowed_scope_paths,
)

watched_paths = [
  OUTPUT_DIR,
  ROOT / "results" / "backtests",
  ROOT / "results" / "trades",
  ROOT / "config" / "runtime.json",
  ROOT / "config" / "strategy",
  ROOT / "logs" / "config_audit.jsonl",
  ROOT / "cache",
]
pre_snapshot = module._snapshot_path_entries(watched_paths)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

candidate_1435_payload = json.loads(CANDIDATE_1435.read_text(encoding="utf-8"))
baseline_source = candidate_1435_payload["metadata"]["baseline_source"]

baseline_cfg = module._load_effective_config(BASELINE_090)
candidate_900_cfg = module._load_effective_config(CANDIDATE_900)
candidate_1435_cfg = module._load_effective_config(CANDIDATE_1435)
always_100_cfg = module._clone_config_with_threshold(candidate_900_cfg, 0.0)

summary = {
  "git_sha": git_sha,
  "packet_base_sha": BASE_SHA,
  "execution_basis_note": execution_basis_note,
  "symbol": "tBTCUSD",
  "timeframe": "3h",
  "threshold": 1435.20957,
  "baseline_source": module._relative_path(BASELINE_090),
  "candidate_900_source": module._relative_path(CANDIDATE_900),
  "candidate_1435_source": module._relative_path(CANDIDATE_1435),
  "helper_surface": module._relative_path(HELPER),
  "years": {},
}
for year in ["2024", "2025"]:
  summary["years"][year] = module._build_year_summary(
    year=year,
    symbol="tBTCUSD",
    timeframe="3h",
    baseline_cfg=baseline_cfg,
    candidate_900_cfg=candidate_900_cfg,
    candidate_1435_cfg=candidate_1435_cfg,
    always_100_cfg=always_100_cfg,
  )
summary["recommendation"] = module._build_recommendation(summary)

SUMMARY_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

y2024 = summary["years"]["2024"]
y2025 = summary["years"]["2025"]
closeout_lines = [
  "# Current-ATR 1435 default-off trial",
  "",
  "Date: 2026-04-16",
  "Mode: RESEARCH",
  f"Execution HEAD: `{git_sha}`",
  "",
  "## Purpose",
  "",
  "Run a bounded execution-only default-off trial on the already implemented `current_atr >= 1435.209570` seam without changing runtime code.",
  "",
  "## Execution basis",
  "",
  f"- packet base SHA: `{BASE_SHA}`",
  f"- actual execution HEAD: `{git_sha}`",
  f"- mixed-basis note: `{execution_basis_note or 'packet base matched execution HEAD'}`",
  "",
  "## Locked inputs",
  "",
  f"- baseline `0.90`: `{module._relative_path(BASELINE_090)}`",
  f"- candidate `900`: `{module._relative_path(CANDIDATE_900)}`",
  f"- candidate `1435`: `{module._relative_path(CANDIDATE_1435)}`",
  f"- helper surface: `{module._relative_path(HELPER)}`",
  "",
  "## 2024",
  "",
  f"- baseline score=`{y2024['variants']['baseline_090']['score']:.4f}`, total_pnl=`{y2024['variants']['baseline_090']['total_pnl']:.4f}`",
  f"- candidate 900 score=`{y2024['variants']['candidate_900']['score']:.4f}`, total_pnl=`{y2024['variants']['candidate_900']['total_pnl']:.4f}`",
  f"- candidate 1435 score=`{y2024['variants']['candidate_1435']['score']:.4f}`, total_pnl=`{y2024['variants']['candidate_1435']['total_pnl']:.4f}`",
  f"- active rows: 1435=`{y2024['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_1435_active_count']}`, 900=`{y2024['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_900_active_count']}`",
  "",
  "## 2025",
  "",
  f"- baseline score=`{y2025['variants']['baseline_090']['score']:.4f}`, total_pnl=`{y2025['variants']['baseline_090']['total_pnl']:.4f}`",
  f"- candidate 900 score=`{y2025['variants']['candidate_900']['score']:.4f}`, total_pnl=`{y2025['variants']['candidate_900']['total_pnl']:.4f}`",
  f"- candidate 1435 score=`{y2025['variants']['candidate_1435']['score']:.4f}`, total_pnl=`{y2025['variants']['candidate_1435']['total_pnl']:.4f}`",
  f"- active rows: 1435=`{y2025['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_1435_active_count']}`, 900=`{y2025['candidate_1435']['override_activation_comparison_vs_candidate_900']['candidate_900_active_count']}`",
  "",
  "## Recommendation",
  "",
  f"- `{summary['recommendation']['recommendation']}`",
  f"- {summary['recommendation']['rationale']}",
  "",
  "## Evidence discipline",
  "",
  "- This is execution-only research evidence on an already implemented seam.",
  "- It does not authorize source-code changes or default promotion.",
  "- It does not claim that 1435 is universally superior to 900.",
]
CLOSEOUT_OUT.write_text("\n".join(closeout_lines) + "\n", encoding="utf-8")

post_snapshot = module._snapshot_path_entries(watched_paths)
diff_events = module._diff_snapshots(pre_snapshot, post_snapshot)
post_git_status_short = module._get_git_status_short()
approved_rel = [module._relative_path(path) for path in approved_files]
unexpected_events = [event for event in diff_events if event["path"] not in approved_rel]
manifest = {
  "git_sha": git_sha,
  "packet_base_sha": BASE_SHA,
  "execution_basis_note": execution_basis_note,
  "command_line": [sys.executable, "-"],
  "effective_env": EXPECTED_ENV,
  "read_only_inputs": {
    "helper_surface": module._relative_path(HELPER),
    "baseline_090": module._relative_path(BASELINE_090),
    "candidate_900": module._relative_path(CANDIDATE_900),
    "candidate_1435": module._relative_path(CANDIDATE_1435),
  },
  "approved_output_dir": module._relative_path(OUTPUT_DIR),
  "approved_output_files": approved_rel,
  "written_files": approved_rel,
  "preflight_git_status_short": pre_git_status_short,
  "postflight_git_status_short": post_git_status_short,
  "containment": {
    "verdict": "PASS" if not unexpected_events else "FAIL",
    "events": diff_events,
    "unexpected_events": unexpected_events,
    "allowed_change_rule": "Only manifest.json, trial_summary.json, and closeout.md may be created or modified in the approved output root.",
  },
  "evidence_note": "This trial is execution-only research evidence on an already implemented seam.",
}
MANIFEST_OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
json.loads(SUMMARY_OUT.read_text(encoding="utf-8"))
actual_files = sorted(path.name for path in OUTPUT_DIR.iterdir() if path.is_file())
if actual_files != ["closeout.md", "manifest.json", "trial_summary.json"]:
  raise SystemExit(f"Unexpected output set: {actual_files}")
if unexpected_events:
  raise SystemExit(f"Containment failure: {unexpected_events}")
print(json.dumps({
  "git_sha": git_sha,
  "execution_basis_note": execution_basis_note,
  "output_dir": str(OUTPUT_DIR),
  "approved_files": actual_files,
}, indent=2))
'@
$trialCode | C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -
```

### Explicit post-write containment validation

The bounded execution command above is itself responsible for all of the following fail-closed checks before returning success:

- `manifest.json` parses successfully as JSON
- `trial_summary.json` parses successfully as JSON
- the approved output root contains exactly:
  - `manifest.json`
  - `trial_summary.json`
  - `closeout.md`
- no unexpected write event appears outside those three approved files, including under:
  - `results/backtests/`
  - `results/trades/`

## Approved outputs

Write only these files under:

- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_1435_default_off_trial_2026-04-16/`

Artifacts:

1. `manifest.json`
2. `trial_summary.json`
3. `closeout.md`

No additional decision-row dumps, no config rewrite, and no uncontrolled `results/backtests/` or `results/trades/` writes are allowed in this slice.

## Gates required

- `pre-commit run --files docs/decisions/current_atr_1435_default_off_trial_packet_2026-04-16.md`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_absent_matches_explicit_disabled tests/utils/test_decision_sizing.py::test_apply_sizing_current_atr_selective_override_replaces_high_vol_multiplier tests/governance/test_config_schema_backcompat.py::test_validate_current_atr_selective_override_absent_matches_explicit_false_leaf`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- bounded execution command using canonical env flags and writing only the approved outputs
- post-write validation that `manifest.json` and `trial_summary.json` both parse successfully as JSON, that the output root contains exactly the three approved files, and that no unexpected write appears outside the approved output root

## Stop Conditions

- any need to edit `src/**`, `tests/**`, `config/**`, or `tmp/**`
- any write outside the approved output root
- any missing or malformed canonical env requirement
- any determinism/hash regression in the required gates
- any wording drift that claims `1435` is universally superior to `900`
- any wording drift that upgrades the result to rollout readiness or default-promotion authority

## Done criteria

This slice is done only if all conditions are met:

1. The packet exists and stays within Scope IN/OUT.
2. The required parity and invariance gates pass.
3. The execution completes without editing code, tests, config, or tmp surfaces.
4. Only the three approved output files are written in the approved output root.
5. `manifest.json` records actual execution basis, canonical env values, locked read-only inputs, and containment verdict.
6. `trial_summary.json` and `closeout.md` state explicitly that `1435` remains a bounded trial candidate, not a universal winner over `900`.
7. `manifest.json` and `closeout.md` preserve mixed execution-basis wording and use `rebased execution basis` language if actual HEAD differs from `e578898448711ad5b2aeca1d2ad3a3bef7342e54`.
8. Any need for code/config/test/tmp edits is reported as a stop-and-reopen condition rather than being absorbed into this slice.

## Evidence wording discipline

- This slice is execution-only research evidence on an already implemented seam.
- It does not authorize source-code changes.
- It does not promote runtime defaults.
- It does not claim that `1435` is universally better than `900`.
- It may state only that `1435` is the first execution-only default-off trial candidate because it is narrower and stronger on blind `2025`, while `900` remains the stronger bounded candidate on `2024`.
