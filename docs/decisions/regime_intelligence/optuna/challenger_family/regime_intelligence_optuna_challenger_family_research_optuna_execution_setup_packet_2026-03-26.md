# Regime Intelligence challenger family — research / Optuna execution setup packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `föreslagen / execution setup only / not run authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines a bounded execution setup for one RI-family-internal Optuna research run, but remains docs-only and must not authorize execution, comparison, readiness, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Define one bounded RI research / Optuna execution setup anchored to the slice8 RI research YAML, including admissible inputs, required preconditions, existing repo-authoritative validation/preflight references, and bounded research-only outputs.
- **Candidate:** `slice8 RI research execution setup`
- **Base SHA:** `3ecaf3a2`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `No execution approval implied`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Consulted for exclusion only:** `backtest_run` — not the active skill here because this packet does not launch a manual backtest
- **Not applied:** `genesis_backtest_verify` — no deterministic artifact comparison is performed by this packet

### Scope

- **Scope IN:**
  - create one docs-only packet that defines the first RI research / Optuna execution setup inside the already-open RI research lane
  - anchor the setup to `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - record the admissible input surface, preflight/validation discipline, storage/resume discipline, baseline-test requirement, and bounded research-only output surface
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no actual Optuna launch
  - no comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_execution_setup_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain subordinate to the already-open RI research lane
- no sentence may authorize or imply an actual launch
- no sentence may define new env/config semantics
- no sentence may reopen comparison, readiness, or promotion
- no sentence may turn the bridge artifact into merit, parity, readiness, or promotion evidence

### Stop Conditions

- any wording that sounds like run approval instead of execution setup
- any wording that upgrades bridge execution-proof into comparison, readiness, or promotion support
- any wording that defines new env/config flag semantics rather than referencing existing repo authority
- any wording that broadens the lane beyond RI-family-internal research
- any need to modify files outside the one scoped packet

### Output required

- reviewable RI research / Optuna execution setup packet
- explicit anchor config and admissible input surface
- explicit preconditions for any later launch attempt
- explicit bounded command shape for a future run setup
- explicit research-only outputs and disallowed claims

## Purpose

This packet defines only a **governed execution setup** for one bounded RI-family-internal Optuna research run.

This packet does **not** approve execution, perform execution, reopen comparison, reopen readiness,
reopen promotion, or upgrade any artifact into runtime or merit authority.

Fail-closed interpretation:

> This packet defines only a governed execution setup for a bounded RI-family-internal Optuna
> research run. The packet itself does not authorize launch, perform any launch, reopen
> comparison/readiness/promotion, or upgrade any artifact into runtime approval, merit evidence,
> or champion authority.

## Upstream governed basis

This packet is downstream of the following already tracked decisions:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_terminal_closeout_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_runtime_bridge_classification_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`

Carried-forward meaning from those packets:

1. the original raw-slice8 comparison/readiness lane is closed
2. the bridge artifact is a derived runtime representation only
3. the bridge artifact remains execution-proof only
4. the next admissible lane is already fixed as **Research lane**
5. all outputs under this lane must remain RI-family-internal research artifacts only

## Research execution subject and anchor

The subject of this setup is one bounded RI-family-internal Optuna research run anchored to:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This anchor may be used only to:

- continue RI-family research within the already-open research lane
- preserve the bounded slice8 research neighborhood
- generate RI-family-internal research artifacts under existing repo runtime/family guardrails

This anchor may **not** be used by this packet to claim:

- incumbent superiority or inferiority
- comparison readiness
- promotion readiness
- champion replacement suitability

## Admissible input surface

Only the following inputs are admissible under this execution setup.

### 1. RI research anchor YAML

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

Allowed use:

- define the research search surface
- define sample and validation windows
- define storage/resume expectations already encoded in the YAML

### 2. Runtime bridge artifact

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Allowed use is strictly limited to the bounded execution question:

- `RI is runnable`

The runtime-valid derived bridge configuration may be cited only for the bounded execution
question `RI is runnable`. It may not be used for merit comparison, normalization, readiness,
promotion, or to create a new evidence class.

### 3. Existing repo-authoritative validation and preflight scripts

- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`

Allowed use:

- reference the existing repo validation and preflight entrypoints that must pass before any later
  long Optuna launch under this setup

This packet does not define new script semantics. It only references existing repo-authoritative
entrypoints.

### 4. Existing RI family guardrails

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

Allowed use:

- constrain any later RI-family execution setup to runtime-valid family semantics
- explain why research admission and runtime validation are related but not identical surfaces

## Required preconditions for any later launch attempt

Any later attempt to launch an RI Optuna run under this setup is blocked unless all of the
following are true.

1. this packet remains unchanged in meaning and still subordinate to the RI research lane
2. the working tree is clean before launch so provenance stays reviewable
3. the anchor YAML still exists at:
   - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
4. config validation passes with exit code `0` using the existing repo entrypoint:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
5. preflight passes with exit code `0` using the existing repo entrypoint:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
6. the baseline-test requirement from `optuna_run_guardrails` is satisfied and recorded before any
   long run is initiated
7. because the anchor YAML sets `resume: false`, the configured storage DB must not be silently
   reused if it already exists:
   - `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db`
8. if the configured storage DB already exists, launch is blocked until one of the following is
   done outside this packet:
   - the DB is removed intentionally, or
   - a separately logged fresh storage target is used
9. any later operator must record the actual launch-session flag/env surface used; any values
   listed here are recorded only as a reproducibility/logging surface for this setup and do not
   create new env/config authority; authoritative semantics remain with the referenced repo
   scripts, YAML, and any separately tracked launch authorization:
   - `GENESIS_FAST_WINDOW=1`
   - `GENESIS_PRECOMPUTE_FEATURES=1`
   - `GENESIS_RANDOM_SEED=42`
   - `GENESIS_FAST_HASH=0`
   - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
   - `PYTHONPATH=src`
   - `PYTHONIOENCODING=utf-8`
   - `TQDM_DISABLE=1`
10. any later launch remains RI-family-internal research only and is logged as such

## Baseline requirement before any long run

`optuna_run_guardrails` requires a baseline test before a long Optuna run.

For this execution setup, that means a later launch operator must first perform and record a
bounded baseline verification of the selected RI research anchor surface before starting a long
Optuna campaign.

This packet does not decide the baseline result. It only makes the baseline requirement mandatory
and traceable before a long run may proceed.

Any such baseline remains:

- RI-family-internal only
- research-only
- non-comparison
- non-readiness
- non-promotion

## Governed execution setup shape (not run authorization)

This section records the bounded command shape for a later RI research launch.

It is **not** a launch approval.

If a later separately tracked step explicitly authorizes launch using this setup, the bounded
launch shape is:

- validation:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- preflight:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- launch shape:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

The launch shape above is bounded by the preconditions in this packet and by the already-open
research lane only.

It must not be read as approval to execute now.

## Expected outputs from any later run under this setup

If a later step explicitly uses this setup for an actual run, the outputs remain limited to
RI-family-internal research artifacts such as:

1. Optuna study artifacts under `results/hparam_search/...`
2. validation artifacts under `results/hparam_search/.../validation/...`
3. RI research summaries tied to the run provenance
4. RI candidate artifacts that remain research-only unless separately governed later

## Bounded claims and disallowed claims

### Allowed claims

- `This execution setup preserves the already-open RI research lane`
- `This setup references the existing repo validation and preflight entrypoints`
- `The bridge artifact may support only the bounded claim that RI is runnable`
- `Any later outputs remain RI-family-internal research artifacts only`

### Disallowed claims

- `This packet approves an Optuna launch`
- `This packet proves RI has beaten the incumbent`
- `This packet reopens comparison`
- `This packet reopens readiness`
- `This packet reopens promotion`
- `This packet upgrades the bridge artifact into merit or readiness evidence`
- `This packet defines new env/config authority`

## Stop conditions for later use of this setup

Any later use of this setup must stop immediately if any of the following occurs:

- validation fails
- preflight fails
- a baseline requirement is skipped
- the storage DB would be reused despite `resume: false`
- the launch drifts outside RI-family-internal research
- a result is framed as comparison, readiness, or promotion evidence
- any operator needs to change repo files to make the launch work

## Bottom line

This packet creates only a **governed RI research / Optuna execution setup**.

It does not authorize execution.

It records the bounded anchor, admissible inputs, required preconditions, existing repo script
references, and research-only output rules that must remain in force if a later separately tracked
step chooses to launch an RI Optuna run inside the already-open research lane.
