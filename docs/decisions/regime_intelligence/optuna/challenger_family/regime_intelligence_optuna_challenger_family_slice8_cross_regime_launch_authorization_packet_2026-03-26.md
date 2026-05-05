# Regime Intelligence challenger family — slice8 cross-regime launch authorization packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical state-bound launch snapshot / branch-specific / no active execution authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records a point-in-time state-bound launch decision on `feature/ri-role-map-implementation-2026-03-24`, not an active launch authority on `feature/next-slice-2026-05-05`.
> - Its own fail-closed and self-revoking conditions tie the decision to the exact verified local state recorded in this packet.
> - Preserve this file as historical launch provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records a separate launch-authorization decision for one exact cross-regime OOS replay config under currently verified local state, but must remain docs-only and must not reopen comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Convert the already-open cross-regime setup-only surface into a separate governed launch decision for the exact OOS replay config under the currently verified local state.
- **Candidate:** `slice8 cross-regime launch authorization`
- **Base SHA:** `9956a73c`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet is prerequisite input only`
- `Authorization is exact-config and exact-state bound`
- `No comparison/readiness/promotion reopening`
- `No new env/config semantics`

### Skill usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `.github/skills/optuna_run_guardrails.json`
- **Supporting repo reference:** `docs/templates/skills/optuna_run_guardrails.md`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Not applied:** any comparison, readiness, or promotion skill surface; this packet remains research-only and authorizes no broader decision class

### Scope

- **Scope IN:**
  - exactly one docs-only launch-authorization packet under `docs/governance/`
  - explicit yes/no decision on whether launch is authorized now for the exact OOS replay config only
  - explicit evidence matrix covering clean tree, exact config identity, `resume=false`, validator exit `0`, preflight green, canonical env surface, storage/resume sanity, and additive config provenance
  - explicit research-only run boundary and self-revoking authorization language
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no actual launch in this slice
  - no reinterpretation of setup-only as lane-wide approval
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_cross_regime_launch_authorization_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate launch-authorization artifact
- no sentence may authorize any config other than the exact replay config named below
- no sentence may turn expected preflight warnings into quality or readiness proof
- no sentence may reopen comparison, readiness, promotion, or writeback
- no sentence may turn current local storage state into a standing repo policy

### Stop Conditions

- any wording that makes the authorization general for slice8 or cross-regime work rather than exact-config and exact-state bound
- any wording that upgrades the research launch into comparison, readiness, or promotion evidence
- any wording that treats expected preflight warnings as proof of quality rather than non-blocking operational context
- any wording that turns local DB absence into general storage policy
- any need to modify files outside this one scoped packet

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit evidence matrix
- explicit research-only run boundary
- explicit self-revoking clause
- explicit output discipline and disallowed claims

## Purpose

This packet records a **separate launch-authorization decision** for the already-open slice8 cross-regime OOS replay surface.

This packet does **not** reinterpret the setup-only packet as launch approval by itself.
It uses the setup-only packet and the committed additive config only as prerequisite inputs to a distinct launch-authorization assessment.

Fail-closed interpretation:

> This packet grants authorization only for the exact replay config named below, only under the
> explicitly verified local state recorded in this packet, and only for a research-only launch
> inside the already-open RI lane. It does not authorize any other YAML, any other storage/resume
> state, or any comparison/readiness/promotion interpretation.

## Upstream governed basis

This packet is downstream of the following already tracked documents and artifacts:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_cross_regime_setup_only_packet_2026-03-26.md`
- commit `9956a73c` adding `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_cross_regime_oos_2025_v1.yaml`

Carried-forward meaning from those steps:

1. the active lane remains RI-family-internal research only
2. the active subject remains the reproduced slice8 full tuple
3. the cross-regime OOS window remains bounded to the exact fixed 2025 replay config named below
4. comparison, readiness, promotion, and writeback remain outside the active lane
5. the setup-only packet remains prerequisite input only and not launch approval by itself

## Exact launch subject

The exact launch subject evaluated by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_cross_regime_oos_2025_v1.yaml`

This packet authorizes or declines launch only for that exact research-only OOS replay config.

No other YAML, alternate storage profile, alternate window, or widened cross-regime surface is authorized by implication.

## Authorization verdict

### Decision

- **AUTHORIZED NOW**

### Exact meaning of this decision

`AUTHORIZED NOW` applies only to:

- the exact config path named above
- a research-only launch inside the already-open RI lane
- the currently verified local state documented in this packet

This does **not** mean:

- slice8 or cross-regime work is generally cleared beyond this exact config
- any alternate YAML is cleared
- comparison, readiness, promotion, or writeback are opened
- a launch has already been executed by this packet

## Evidence matrix for the current verified state

| Check | Required state | Current state | Evidence basis | Result |
| --- | --- | --- | --- | --- |
| Working tree clean | Green | No changes detected | session `git status --short` produced no output after commit `9956a73c` | Green |
| Exact config identity | Stable exact subject | Exact replay config present | `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_cross_regime_oos_2025_v1.yaml` | Green |
| Additive config provenance | Tracked and bounded | Config committed as additive research-only slice | commit `9956a73c` — `tooling(ri): add slice8 cross-regime OOS config` | Green |
| `resume=false` | Explicit fresh-run intent | `resume: false` present in exact config | exact config contents reviewed in session | Green |
| Config validation | Explicit green | Exit code `0` captured this session | terminal session captured `VALIDATE_EXIT:0` for the exact config under canonical env surface | Green |
| Preflight | Explicit green | Passed this session | `scripts/preflight/preflight_optuna_check.py` reported `[OK] Alla preflight-checkar passerade - Optuna bör kunna köras` for the exact config | Green |
| Canonical env surface | Match required research surface | Canonical env surface applied in validation/preflight session | session used `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_HASH=0`, `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`, `PYTHONPATH=src`, `PYTHONIOENCODING=utf-8`, `TQDM_DISABLE=1`, `OPTUNA_MAX_DUPLICATE_STREAK=2000` | Green |
| Expected preflight warnings | Non-blocking only | Observed and non-blocking for this replay surface | preflight reported fixed-parameter and low-startup-trial warnings only; no fail condition resulted | Green |
| Storage/resume sanity | No silent reuse under `resume=false` | Expected local DB path absent at review time | `Test-Path` on `results/hparam_search/storage/ri_challenger_family_slice8_cross_regime_oos_2025_v1.db` returned `False` | Green |

## Why `AUTHORIZED NOW` is fail-closed and still safe

This verdict is governance-safe because the currently required launch conditions for this exact config are satisfied in documented local state:

1. tracked working tree cleanliness has been restored after the additive config commit
2. config validation has an explicit green exit signal in this session
3. preflight has passed in this session under the canonical env surface
4. the exact config itself carries `resume=false`
5. the expected local study DB path is absent, which supports only the narrow claim that a launch from the current verified local state would start fresh rather than resume from that specific local DB path

The observed preflight warnings are **expected and non-blocking** for this replay surface.
They do **not** widen this authorization, do **not** prove quality, and do **not** create readiness or promotion evidence.

## Research-only run boundary

Any launch eventually taken under this authorization remains strictly bounded as follows.

### Allowed boundary

- research only
- RI-family-internal only
- exact OOS replay config only
- bounded to the already-open cross-regime slice8 question/setup surface

### Disallowed boundary

- no incumbent comparison claims
- no readiness claims
- no promotion claims
- no champion replacement claims
- no writeback claims

This packet does not widen any claim beyond the already-open research lane.

## Self-revoking clause

This authorization self-revokes immediately if any of the following changes before launch:

- the working tree is no longer clean
- the exact replay config changes or is substituted
- the canonical env surface changes from the verified surface cited above
- validation or preflight no longer correspond to the cited green state
- the expected local DB path becomes present such that silent reuse under `resume=false` could become possible again
- any comparison, readiness, promotion, or writeback framing is introduced

If any of those conditions occurs, this packet must no longer be treated as active launch authorization.

## Output handling and artifact discipline after any later launch

If a later operational step uses this authorization to perform the run, output handling remains bounded as follows.

### Raw artifacts

Raw run artifacts may appear only as RI-family-internal research artifacts under local research output paths such as:

- `results/hparam_search/...`
- `results/hparam_search/storage/...`

These artifacts are not by themselves comparison, readiness, or promotion proof.

### Required provenance capture

Any later run report must capture at minimum:

- exact config path launched
- git commit used for the run
- study name and storage path actually used
- sample window actually used
- actual effective env/flag surface used at launch time
- outcome of validation and preflight prerequisites

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

This packet records a separate governed launch decision for the exact slice8 cross-regime OOS replay config.

That decision is:

- **AUTHORIZED NOW**

But only for:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_cross_regime_oos_2025_v1.yaml`
- the exact verified local state documented in this packet
- a research-only launch that remains inside the already-open RI lane

It is a narrow, state-bound, self-revoking authorization and nothing broader.
