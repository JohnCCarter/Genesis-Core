# Regime Intelligence challenger family — slice8 structural search-space management/override design authorization packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `design-authorization only / exact config surface and ranges selected / no launch authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet is sensitive only in governance-signaling terms because it binds the already chosen bounded management/override seam to one exact future config surface and one exact range set, but it remains exactly one docs-only file with no runtime, config, schema, env, or high-sensitivity code changes.
- **Required Path:** `Quick`
- **Objective:** Bind the chosen bounded management/override seam to one exact additive config surface and one exact range set for a later separate materialization, validation/preflight, and launch process, while keeping the current objective/version/metric surface fixed and authorizing no launch.
- **Candidate:** `slice10 structural management/override design authorization`
- **Base SHA:** `d3af485c`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Design-authorization only / non-authorizing for launch`
- `Materialization only / no validation success implied`
- `No config materialization in this packet`
- `No objective-change opening`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill usage

- No repository skill is evidenced for this docs-only design-authorization packet.
- Guardrail surfaces may be cited only as future references for later config validation, preflight, and launch steps.
- Any future skill coverage for config materialization or launch remains `föreslagen` until implemented and verified.

### Scope

- **Scope IN:**
  - exactly one docs-only packet under `docs/governance/`
  - explicit selection of one exact future config materialization target:
    - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
  - explicit exact ranges copied from the already governed slice9 management/override seam:
    - `exit.max_hold_bars`: `7..9 step 1`
    - `exit.exit_conf_threshold`: `0.40..0.44 step 0.01`
    - `multi_timeframe.ltf_override_threshold`: `0.38..0.42 step 0.01`
  - explicit donor-surface rule that future materialization must use `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml` as the immediate donor for backbone, fixed fields, and windows, with only the explicitly authorized differences listed here
  - explicit statement that future materialization remains additive and dormant unless separately validated and launched
  - explicit statement that the current objective/version/metric surface remains fixed
- **Scope OUT:**
  - no source-code changes
  - no `tests/**`, `config/**`, or `results/**` changes in this packet
  - no config materialization in this packet
  - no launch authorization
  - no actual replay or Optuna execution
  - no parameter widening beyond the exact ranges above
  - no alternate seam selection
  - no objective-change opening
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no runtime/default/env/config-authority change
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_management_override_design_authorization_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must authorize only future additive materialization of the exact slice10 YAML named here
- no sentence may imply validator success, preflight success, launch approval, or execution approval
- no sentence may widen the chosen seam beyond the exact three axes and exact ranges listed here
- no sentence may loosen the donor-surface rule into a generic `slice8 backbone` interpretation
- no sentence may reopen objective design or imply that objective v2 is inadequate

### Stop Conditions

- any wording that treats this packet as config creation rather than design authorization only
- any wording that treats this packet as validation, preflight, or launch approval
- any wording that selects alternate ranges, alternate seams, or alternate config paths
- any wording that reopens objective design, incumbent comparison, readiness, promotion, or writeback
- any need to modify files outside this one scoped packet

### Output required

- reviewable design-authorization packet
- explicit future config materialization target
- explicit exact ranges
- explicit donor-surface rule
- explicit statement that launch and execution remain out of scope

## Purpose

This packet answers one narrow question only:

- what exact future config surface and what exact ranges are authorized for later additive materialization inside the already-open slice8 structural-search-space lane?

This packet authorizes only future additive materialization of the exact slice10 YAML named below.
It does **not** authorize config validation success, preflight success, launch, execution, objective redesign, comparison, readiness, promotion, or writeback.

Fail-closed interpretation:

> This packet authorizes only future additive materialization of one exact optimizer YAML and
> one exact set of management/override ranges. It does not create the YAML, does not prove
> validator or preflight success, does not authorize launch or execution, and does not reopen
> objective/version/metric, comparison, readiness, promotion, or writeback.

## Governing basis

This packet is downstream of the following already tracked documents:

- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_research_question_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_setup_only_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_seam_decision_packet_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`

Carried-forward meaning from those documents:

1. the active lane remains RI-family-internal research only
2. the bounded management/override seam is already the chosen seam
3. the gating/selectivity seam is not chosen now but is not permanently vetoed
4. the exact frozen slice8 tuple failed the bounded 2025 cross-regime replay
5. slice9 provided bounded management/override evidence around the slice8 backbone
6. the current objective/version/metric surface remains fixed unless a separate later packet reopens it

## Exact future config materialization target

The only exact future config materialization target authorized by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`

This packet authorizes only the future additive creation of that exact YAML path in a later separate config-materialization step.

It does **not** authorize:

- creation of any alternate YAML path
- mutation of any existing slice YAML
- config-path reservation beyond the exact target above
- any launch or execution using that path

## Exact seam and exact ranges authorized for later materialization

The only exact seam and exact ranges authorized for later materialization are:

- `exit.max_hold_bars`: `7..9 step 1`
- `exit.exit_conf_threshold`: `0.40..0.44 step 0.01`
- `multi_timeframe.ltf_override_threshold`: `0.38..0.42 step 0.01`

These ranges are authorized only because they are already the exact ranges evidenced in:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`

This packet does **not** authorize any alternate widening, narrowing, or sampler redesign.

## Donor-surface rule for later materialization

Any later materialization of the exact slice10 YAML authorized by this packet must use the following file as the immediate donor surface:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`

The donor-surface rule means:

- backbone, fixed fields, sample/validation windows, score version, run intent, and fixed RI-family identity fields must be copied from the slice9 YAML
- only the following differences are authorized in that later materialization step:
  - fresh study/storage names for slice10
  - the exact target path named above
  - the same three management/override ranges listed above
  - descriptive comments or description text necessary to reflect slice10 provenance

This rule exists to prevent ambiguous interpretation of `slice8 backbone` as a freehand reconstruction.

## Dormant-status boundary

The later slice10 YAML authorized for materialization here must remain dormant by default unless separately validated and separately launched.

For authorization purposes only, the later slice10 YAML is to be treated as additive and non-launching by itself unless a later phase explicitly adds it to a selector, manifest, batch list, or launch surface.

This packet does not certify repository-wide auto-discovery behavior and does not replace separate validation or launch authorization.

This packet does **not** authorize modifying any selector, manifest, scheduler, batch surface, or launch list.

## Objective/version/metric boundary

The current objective/version/metric surface remains fixed.

This packet does **not** reopen:

- objective v2
- any new metric design
- any new pass/fail threshold
- any comparison, readiness, promotion, or writeback lane

## Future validation and launch remain separate

Any later config-materialization step, validator/preflight step, and launch-authorization step remain separate later phases.

This packet does **not** claim:

- that the later slice10 YAML will validate successfully
- that the later slice10 YAML will pass preflight
- that the later slice10 YAML is launch-ready
- that any run should begin now

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- actual YAML creation
- validator execution
- preflight execution
- launch authorization
- actual replay or Optuna execution
- result interpretation
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback

## Bottom line

This packet authorizes only one later additive config materialization inside the slice8 structural-search-space lane:

- target YAML: `tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`
- donor surface: `tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- exact authorized seam: bounded management/override seam
- exact authorized ranges:
  - `exit.max_hold_bars`: `7..9 step 1`
  - `exit.exit_conf_threshold`: `0.40..0.44 step 0.01`
  - `multi_timeframe.ltf_override_threshold`: `0.38..0.42 step 0.01`

No YAML is created by this packet, no validation is implied, and no launch or execution is authorized here.
