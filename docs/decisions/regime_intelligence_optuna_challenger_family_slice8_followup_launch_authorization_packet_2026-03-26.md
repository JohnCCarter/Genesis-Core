# Regime Intelligence challenger family — slice8 follow-up launch authorization packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch authorization decision recorded / fail-closed / authorized now under exact verified state`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records a separate launch-authorization decision for the already-open slice8-first follow-up RI research lane, but must remain docs-only and must not reopen comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Convert the already-open slice8-first follow-up setup-only surface into a separate governed launch decision for the exact slice8 anchor under the currently verified local state.
- **Candidate:** `slice8-first follow-up launch authorization`
- **Base SHA:** `34a843fd`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet is prerequisite input only`
- `Authorization is exact-anchor and exact-state bound`
- `No comparison/readiness/promotion reopening`
- `No new env/config semantics`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/templates/skills/optuna_run_guardrails.md`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Not applied:** any comparison, readiness, or promotion skill surface; this packet remains research-only and authorizes no broader decision class

### Scope

- **Scope IN:**
  - one docs-only launch-authorization packet for the already-open slice8-first follow-up research lane
  - explicit yes/no decision on whether launch is authorized now for the exact slice8 anchor only
  - explicit evidence matrix covering clean tree, exact anchor identity, validation, preflight, storage/resume sanity, and smoke provenance
  - explicit research-only run boundary and self-revoking authorization language
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no actual Optuna launch
  - no reinterpretation of setup-only as implicit lane-wide approval
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate launch-authorization artifact
- no sentence may treat the setup-only packet as lane-wide or future-general approval
- no sentence may authorize any YAML other than the exact anchor named below
- no sentence may reopen comparison, readiness, promotion, or writeback
- no sentence may turn local state-restoration into repo policy or a new evidence class

### Stop Conditions

- any wording that collapses setup and launch authorization into the same decision
- any wording that makes the authorization general for slice8-family work rather than exact-anchor and exact-state bound
- any wording that upgrades the research launch into comparison, readiness, or promotion evidence
- any wording that turns the local DB-preservation action into general storage policy
- any need to modify files outside the one scoped packet

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit evidence matrix
- explicit research-only run boundary
- explicit self-revoking clause
- explicit output discipline and disallowed claims

## Purpose

This packet records a **separate launch-authorization decision** for the already-open slice8-first follow-up RI research lane.

This packet does **not** reinterpret the setup-only packet as launch approval by itself.
It uses the setup-only packet only as prerequisite input to a distinct launch-authorization assessment.

Fail-closed interpretation:

> This packet grants authorization only for the exact slice8 anchor named below, only under the
> explicitly verified local state recorded in this packet, and only for a research-only launch
> inside the already-open RI lane. It does not authorize any other YAML, any other storage/resume
> state, or any comparison/readiness/promotion interpretation.

## Upstream governed basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`

Carried-forward meaning from those packets:

1. the active lane remains RI-family-internal research only
2. slice8 is the sole preferred continuation surface
3. slice9 remains secondary robustness context only
4. slice7 remains historical context only
5. comparison, readiness, promotion, and writeback remain outside the active lane
6. the setup-only packet remains prerequisite input only and not launch approval by itself

## Exact launch subject

The exact launch subject evaluated by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This packet authorizes or declines launch only for that exact RI research / Optuna input artifact.

No other YAML, bridge JSON, derived candidate file, alternate storage profile, or widened slice8-family surface is authorized by implication.

## Authorization verdict

### Decision

- **AUTHORIZED NOW**

### Exact meaning of this decision

`AUTHORIZED NOW` applies only to:

- the exact anchor YAML named above
- a research-only launch inside the already-open slice8-first follow-up lane
- the currently verified local state documented in this packet

This does **not** mean:

- slice8-family work is generally cleared beyond this exact anchor
- any alternate YAML is cleared
- comparison, readiness, promotion, or writeback are opened
- a launch has already been executed by this packet

## Evidence matrix for the current verified state

| Check | Required state | Current state | Evidence basis | Result |
| --- | --- | --- | --- | --- |
| Working tree clean | Green | No tracked changes detected | session `git status --short` produced no tracked changes; `get_changed_files` returned no changed files | Green |
| Exact anchor identity | Stable exact subject | Exact slice8 anchor present | `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml` | Green |
| Config validation | Explicit green | Exit code `0` captured this session | terminal session captured `VALIDATE_EXIT:0` for the exact anchor under canonical env surface | Green |
| Preflight | Explicit green | Passed this session | `scripts/preflight/preflight_optuna_check.py` reported `[OK] Alla preflight-checkar passerade - Optuna bör kunna köras` | Green |
| Canonical env surface | Match required research surface | Canonical env surface applied in validation/preflight session | session used `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_HASH=0`, `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`, `PYTHONPATH=src`, `PYTHONIOENCODING=utf-8`, `TQDM_DISABLE=1`, `OPTUNA_MAX_DUPLICATE_STREAK=2000` | Green |
| Storage/resume sanity | No silent reuse under `resume=false` | Current primary DB conflict neutralized | active path `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db` no longer present; preserved backups exist at `ri_challenger_family_slice8_3h_2024_v1_prelaunch_backup_20260326.db` and `ri_challenger_family_slice8_3h_2024_v1_stateprep_backup_20260326_155532.db` | Green |
| Same-day smoke provenance | Same governed surface | Same-day smoke remains attributable to same slice8 surface | `tmp/ri_slice8_smoke_20260326.yaml` explicitly states it is derived from the slice8 anchor; `results/hparam_search/ri_slice8_smoke_20260326/run_meta.json` and validation artifact match the same snapshot/timeframe/run-intent surface | Green |
| Tracked drift absent | No tracked drift | No tracked drift detected | no changed tracked files reported after state-prep | Green |

## Why `AUTHORIZED NOW` is fail-closed and still safe

This verdict is governance-safe because the currently blocking conditions from the earlier `NOT AUTHORIZED NOW` state have been resolved in documented local state:

1. tracked working tree cleanliness has been restored
2. config validation has an explicit green exit signal in this session
3. preflight has passed in this session under the canonical env surface
4. the `resume=false` storage conflict has been neutralized by a local preservation move rather than silent reuse
5. same-day smoke provenance remains attributable to the same slice8 governed surface

The local DB-preservation action is a **local state-restoration action only**.
It is not a repo change, not a new evidence class, and not a general storage-policy statement.

## Research-only run boundary

Any launch eventually taken under this authorization remains strictly bounded as follows.

### Allowed boundary

- research only
- RI-family-internal only
- exact slice8 anchor only
- bounded to the already-open slice8-first follow-up research lane

### Disallowed boundary

- no incumbent comparison claims
- no readiness claims
- no promotion claims
- no champion replacement claims
- no writeback claims

This packet does not widen the bridge claim or any other claim beyond the already-open research lane.

## Self-revoking clause

This authorization self-revokes immediately if any of the following changes before launch:

- the working tree is no longer clean
- the exact anchor YAML changes or is substituted
- the canonical env surface changes materially from the verified surface cited above
- validation or preflight no longer correspond to the cited green state
- storage state changes such that silent reuse under `resume=false` becomes possible again
- smoke provenance can no longer be tied to the same governed slice8 surface
- any comparison, readiness, promotion, or writeback framing is introduced

If any of those conditions occurs, this packet must no longer be treated as active launch authorization.

## Output handling and artifact discipline after any later launch

If a later separate operational step uses this authorization to perform the run, output handling remains bounded as follows.

### Raw artifacts

Raw run artifacts may appear only as RI-family-internal research artifacts under local research output paths such as:

- `results/hparam_search/...`
- `results/hparam_search/storage/...`
- `results/hparam_search/.../validation/...`

These artifacts are not by themselves comparison, readiness, or promotion proof.

### Required provenance capture

Any later run report must capture at minimum:

- exact config path launched
- git commit used for the run
- study name and storage path actually used
- sample and validation windows
- actual effective env/flag surface used at launch time
- outcome of validation, preflight, and smoke/baseline prerequisites

### Forbidden post-run handling in this lane

- no automatic champion update
- no automatic writeback
- no automatic comparison packet
- no automatic readiness packet
- no automatic promotion packet

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- actual launch execution
- any code/config/runtime change
- any alternate YAML or alternate strategy surface
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback
- any new evidence class

## Bottom line

This packet records a separate governed launch decision for the already-open slice8-first follow-up RI research lane.

That decision is:

- **AUTHORIZED NOW**

But only for:

- the exact slice8 anchor YAML named above
- the exact verified local state documented in this packet
- a research-only launch that remains inside the already-open RI lane

It is a narrow, state-bound, self-revoking authorization and nothing broader.
