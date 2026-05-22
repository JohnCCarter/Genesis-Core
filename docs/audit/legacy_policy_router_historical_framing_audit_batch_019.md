# Batch 019 Legacy policy-router historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for the retained Legacy policy-router packet trio.
> It does **not** reopen current Legacy implementation, execution, runtime, or cross-family
> authority by itself.

## Scope boundary

Primary candidates in scope:

- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md`

Supporting evidence surfaces in scope:

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
- `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`

Out of scope in this batch:

- editing any `docs/decisions/regime_intelligence/**` packet
- editing `GENESIS_WORKING_CONTRACT.md`
- editing any `tmp/**`, `tests/**`, `config/**`, `results/**`, or `src/**` surface named in the retained packets
- rewriting any body content below the top framing block, including scope, constraints, gates, or bottom-line conclusions
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

## Method

Checked in this slice:

- full read of the three retained Legacy policy-router packets
- read of the single clear outside-family citation anchor in the RI payoff-state translation packet
- repo check for exact stale top status strings across tracked docs
- top-of-file status/current-use framing check for all three packet files

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch019_legacy_policy_router_historical_framing_evidence.json`

## Observed

### The trio is branch-local retained Legacy packet provenance with light external coupling

Observed supporting context:

- all three packets are tied to `feature/next-slice-2026-04-29`
- the outside-family citation fan-out is light and mainly points to the surface-separation packet as historical Legacy context
- the current work queue still treats blocked move/reference work as a later concern while smaller docs-only packet hardening remains admissible

### The packet tops still read like open or current slice authority

Observed pre-change top status drift across the trio:

- `legacy_policy_router_surface_separation_precode_packet_2026-04-30.md` began with `pre-code-defined / docs-only / no implementation or execution authority`
- `legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md` began with `pre-code-defined / docs-only / setup-only / no implementation or execution authority`
- `legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md` began with `implemented / config-test-docs / no backtest or runtime execution authority`

Observed skim-risk pattern:

- without a top current-status note, later readers can over-read the retained packets as current
  branch setup or implementation guidance rather than historical branch-local Legacy decision context
- the stale effect is concentrated at the file tops; the bodies already contain bounded historical
  setup/implementation logic that should remain verbatim in this slice

## Inferred

- the safe correction is a **top-framing sync only** that recasts the trio as retained historical
  Legacy policy-router context without rewriting their packet logic
- the safe patch shape in this batch is:
  - replace stale top status labels with historical/current-use framing only
  - add one narrow current-status note near the top of each file
  - explicitly deny current implementation, execution, or cross-family authority in the new top notes
  - preserve all packet bodies, scope boundaries, gates, and conclusions below the framing block

## UNRESOLVED

- `UNRESOLVED:` whether any later bounded slice should historicalize adjacent Legacy policy-router
  families outside this trio
- `UNRESOLVED:` whether any later move/reference work becomes admissible once protected provenance
  surfaces are clean or explicitly reopened

## Batch result summary

- Candidates reviewed: `3`
- `READY_STATUS_HEADER`: `3`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                         | Observed role                                 | Drift signal                                                                                            | Classification        | Safe batch action                       |
| ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------- | --------------------------------------- |
| `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`        | historical Legacy separation pre-code packet  | stale `pre-code-defined / docs-only / no implementation or execution authority` reads live              | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_precode_packet_2026-04-30.md`        | historical Legacy setup pre-code packet       | stale `pre-code-defined / docs-only / setup-only / no implementation or execution authority` reads live | `READY_STATUS_HEADER` | replace status/current-use framing only |
| `docs/decisions/legacy/policy_router/legacy_policy_router_2024_control_setup_implementation_packet_2026-04-30.md` | historical Legacy setup implementation packet | stale `implemented / config-test-docs / no backtest or runtime execution authority` reads live          | `READY_STATUS_HEADER` | replace status/current-use framing only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing blocks of the three retained Legacy policy-router packets

This audit does **not** support changing:

- any referenced `tmp/**`, `tests/**`, `config/**`, `results/**`, or `src/**` surface
- any RI packet that cites the Legacy surface-separation packet
- any scope boundary, gate stack, or conclusion below the top framing block

## Bottom line

Batch 019 is a bounded historical-framing correction for one self-contained Legacy policy-router
packet trio.

The classification applies to header framing only; the bodies remain verbatim historical packet
records and are not re-audited here for current implementation, execution, runtime, or cross-family
authority.
