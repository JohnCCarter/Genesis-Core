# Regime Intelligence challenger family — slice10 structural launch authorization packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `AUTHORIZED NOW / state-bound / self-revoking / research only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records an execution-facing launch decision for one exact RI-family-internal research config, but remains docs-only and must not reopen comparison, readiness, promotion, writeback, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Record a separate launch-authorization decision for the exact committed slice10 structural management/override research subject after exact-subject validator/preflight success and bounded supporting smoke evidence, while keeping the lane strictly RI-family-internal and research-only.
- **Candidate:** `slice10 structural launch authorization`
- **Base SHA:** `309ef51e`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Authorization is subject-bound and self-revoking`
- `No comparison/readiness/promotion/writeback reopening`
- `No execution performed by this packet`
- `No objective/version/metric reopening`
- `No env/config semantics changes`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/templates/skills/optuna_run_guardrails.md`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Consulted for exclusion only:** any comparison/readiness/promotion surface — not active here because this packet authorizes only a bounded RI-family-internal research launch subject

### Scope

- **Scope IN:**
  - exactly one docs-only launch-authorization packet under `docs/governance/`
  - explicit authorization decision for one exact committed launch subject
  - explicit current-green evidence basis from this session
  - explicit state-bound and self-revoking conditions
  - explicit research-only run boundary and output discipline
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes by this packet
  - no actual Optuna execution by this packet
  - no alternate launch subject authorization
  - no reinterpretation of tmp smoke evidence as exact-subject smoke
  - no comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_slice10_structural_launch_authorization_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate launch-authorization artifact
- no sentence may authorize anything except the exact committed slice10 YAML named below
- no sentence may describe the tmp-local smoke YAML as the primary or exact launch subject
- no sentence may reopen comparison, readiness, promotion, writeback, or objective design
- no sentence may imply execution was performed by this packet itself

### Stop Conditions

- any wording that turns supporting tmp smoke evidence into an alternate or co-equal launch subject
- any wording that makes this authorization durable independent of current repo state
- any wording that upgrades research launchability into comparison, readiness, or promotion evidence
- any wording that widens the search seam beyond the already authorized three axes
- any need to modify files outside this one scoped packet

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit exact launch subject and provenance
- explicit current-green evidence basis
- explicit self-revoking clause
- explicit research-only output discipline

## Purpose

This packet records a **separate launch-authorization decision** for one exact RI-family-internal research subject inside the already-open structural search-space lane.

The packet does **not** execute the run, does **not** reopen objective/version/metric design, and does **not** create any comparison, readiness, promotion, or writeback authority.

Fail-closed interpretation:

> This packet authorizes launch only for one exact committed slice10 research YAML on the current
> verified clean launch surface. The packet does not execute the run, does not authorize any
> alternate YAML, does not treat tmp smoke evidence as the primary launch subject, and does not
> reopen comparison, readiness, promotion, writeback, or runtime/default authority.

## Upstream governed basis

This packet is downstream of the following already tracked decisions:

- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_research_question_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_setup_only_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_seam_decision_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_management_override_design_authorization_packet_2026-03-27.md`

Carried-forward meaning from those packets:

1. the lane remains RI-family-internal research only
2. the structural continuation remains bounded to the management/override seam chosen on 2026-03-27
3. the current objective/version/metric surface remains fixed
4. the exact committed slice10 YAML is additive research material only until separately launched
5. no comparison, readiness, promotion, or writeback authority is opened here

## Exact launch subject and provenance

The only launch subject authorized by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`

Exact provenance of that launch subject:

- introduced by commit `309ef51e` — `config(ri): add slice10 structural management config`
- design-authorized upstream by:
  - `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_management_override_design_authorization_packet_2026-03-27.md`

No other YAML is authorized as launch subject by implication, including:

- any edited copy of the committed slice10 YAML
- any tmp-local smoke YAML
- any alternate structural continuation YAML
- any derived runtime/candidate artifact

## Exact seam remains unchanged

This launch authorization is bounded to the already authorized three-axis seam only:

- `exit.max_hold_bars`: `7..9 step 1`
- `exit.exit_conf_threshold`: `0.40..0.44 step 0.01`
- `multi_timeframe.ltf_override_threshold`: `0.38..0.42 step 0.01`

This packet does **not** authorize any widening, narrowing, or redesign of that seam.

## Supporting smoke evidence only

The bounded smoke surface used in this session is supporting launchability evidence only:

- tmp YAML: `tmp/tBTCUSD_3h_ri_challenger_family_slice10_smoke_20260327.yaml`
- tmp storage: `tmp/ri_slice10_smoke_20260327.db`
- smoke run id: `ri_slice10_smoke_20260327`

The supporting smoke YAML was a tmp-local derivative used only to verify launchability under a reduced run budget.

It is **not**:

- the primary launch subject
- an alternate authorized launch subject
- exact-subject end-to-end smoke on the committed YAML path
- evidence of merit, readiness, promotion, or comparison superiority

Equivalence/difference note for the tmp-local smoke derivation:

- semantic RI family identity, symbol, timeframe, snapshot, train/validation windows, run intent, score version, fixed backbone, and the exact three-axis search surface were preserved from the committed slice10 launch subject
- only smoke-operational fields were changed:
  - tmp-local YAML path
  - unique smoke study name
  - unique tmp-local sqlite storage
  - reduced `max_trials` from `75` to `5`
  - reduced `timeout_seconds` from `10800` to `900`
  - explicit smoke `run_id`

## Authorization verdict

### Decision

- **AUTHORIZED NOW**

### Scope of that authorization

This authorization applies **only** to the exact committed launch subject named above, on the current verified clean launch surface recorded in this packet.

This packet authorizes only a research / Optuna launch of that exact named config.
It does **not** alter the RI-family runtime contract, does **not** constitute champion or promotion approval, and does **not** establish any new canonical comparison or materialization surface.

This is not a durable general authorization.
It is a point-in-time, subject-bound, state-bound launch decision.

### Self-revoking clause

This authorization automatically ceases to apply if any of the following occurs before launch:

1. the working tree is no longer clean
2. the launch subject drifts in content or path from the committed `309ef51e` version
3. the target storage path is no longer free for a fresh run under `resume=false`
4. validator or preflight no longer remain green on the exact committed launch subject
5. the canonical env surface used for launch no longer matches the verified surface recorded here

If any of the above occurs, this authorization is void and a new fail-closed review is required.

## Current-green evidence basis observed in this session

### 1. Working tree clean

Observed state:

- `git status --short` returned no output immediately before writing this packet

Governance meaning:

- the clean-working-tree predicate is green on the current launch surface

### 2. Exact-subject config validation green by explicit success outcome

Launch subject validated:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`

Observed state:

- validator completed with warnings only and no hard failure

Interpretation boundary:

- warnings were observed, but the validator completed successfully for the exact committed launch subject and is therefore treated as green for launch-authorization purposes

### 3. Exact-subject preflight green

Launch subject preflighted:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`

Observed state:

- `scripts/preflight/preflight_optuna_check.py` completed green and reported:
  - `[OK] Alla preflight-checkar passerade - Optuna bör kunna köras`

Governance meaning:

- the exact committed launch subject is currently launchable on the verified surface

### 4. Storage path free under `resume=false`

Observed state:

- explicit check returned:
  - `STORAGE_EXISTS=0 results/hparam_search/storage/ri_challenger_family_slice10_3h_2024_v1.db`

Governance meaning:

- the current launch subject does not point at an already-existing primary DB while `resume=false`

### 5. Supporting bounded smoke completed and documented

Supporting smoke evidence paths:

- `results/hparam_search/ri_slice10_smoke_20260327/run_meta.json`
- `results/hparam_search/ri_slice10_smoke_20260327/validation/trial_001.json`

Observed smoke state:

- smoke run completed with exit code `0`
- `run_meta.json` records:
  - `run_id=ri_slice10_smoke_20260327`
  - `git_commit=309ef51edaffd901af8463f5b026af94a3256381`
  - `validated=5`
- `validation/trial_001.json` records:
  - `constraints.ok=true`
  - `num_trades=63`

Interpretation boundary:

- this smoke supports launchability of the committed slice10 research surface only
- it does not upgrade the tmp smoke YAML into a launch subject
- it does not support comparison, readiness, promotion, or writeback claims

### 6. Canonical env surface matched across validator, preflight, and smoke

The following env surface was used consistently in this session:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
- `PYTHONPATH=src`
- `PYTHONIOENCODING=utf-8`
- `TQDM_DISABLE=1`
- `OPTUNA_MAX_DUPLICATE_STREAK=2000`

Governance meaning:

- launch authorization is anchored to the same canonical research surface already used for exact-subject validation and supporting smoke evidence

## Run boundary remains unchanged

Any launch authorized by this packet remains strictly bounded as follows.

### Allowed boundary

- research only
- RI-family-internal only
- bounded to the exact committed slice10 structural management/override subject

### Disallowed boundary

- no comparison claims
- no readiness claims
- no promotion claims
- no champion replacement claims
- no writeback claims
- no objective redesign claims

This packet authorizes only a bounded RI-family-internal research launch.

Any structural research overrides present in the slice10 launch subject remain research-slice-only under the current governance chain.
A positive launch outcome would therefore not by itself make the launch subject runtime-valid RI under the current family-admission or validator contract.

## Output handling and artifact discipline after launch

If launch is executed under this authorization, output handling must remain disciplined as follows.

### Raw run artifacts

Raw run artifacts may remain under the expected local research output area, including:

- `results/hparam_search/...`
- `results/hparam_search/storage/...`
- `results/hparam_search/.../validation/...`

These remain RI-family-internal research artifacts only.
They are not by themselves tracked proof of comparison, readiness, or promotion.

### Required provenance capture

Any launch report must record at minimum:

- exact config path launched
- git commit used for the run
- study name and storage path
- sample and validation windows
- actual launch-session env/flag surface
- outcome of validator, preflight, and supporting smoke prerequisites

### Tracked summary discipline

If any tracked summary is created after launch, it must:

- remain explicitly research-only
- identify the run as RI-family-internal
- avoid comparison, readiness, promotion, and writeback framing
- avoid upgrading supporting smoke evidence into merit or readiness evidence

## Bottom line

This packet records a separate governed launch decision for the slice10 structural RI research lane.

That decision is:

- **AUTHORIZED NOW**

But only for:

- the exact committed launch subject `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
- the current clean launch surface verified in this packet

If that state changes before launch, this authorization no longer applies and a new fail-closed review is required.
