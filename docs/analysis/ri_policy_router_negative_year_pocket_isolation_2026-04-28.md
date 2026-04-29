# RI policy router negative-year pocket isolation

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only isolation / negative-pocket summary recorded`

This slice is a read-only follow-up to the curated annual enabled-vs-absent evidence.
It does not modify runtime/config/schema/authority surfaces and does not authorize tuning, promotion, or any new router packet.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice only analyzes already-generated annual action-diff artifacts and records a docs-only summary.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the annual verdict is already established as mixed, so the next honest question is whether the clearly negative full years share one recurring pocket shape before any further runtime framing is considered.
- **Objective:** isolate the recurring action-diff pocket shape inside the clearly negative curated annual years `2019`, `2021`, and `2024`.
- **Candidate:** `negative-year pocket summary`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Evidence inputs

- `docs/analysis/ri_policy_router_enabled_vs_absent_annual_evidence_2026-04-28.md`
- `docs/analysis/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `tmp/policy_router_evidence/analyze_negative_year_pockets_20260428.py`
- `results/research/ri_policy_router_negative_year_pockets_20260428/negative_year_pocket_summary.json`
- curated annual action-diff files for `2019`, `2021`, and `2024`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_negative_year_pockets_20260428.py`

## Subject boundary

This slice analyzes only the clearly negative full years on the curated annual surface:

- `2019`
- `2021`
- `2024`

A year counted as clearly negative only when enabled was worse than absent on all four top-level axes used in the annual reading:

- return
- profit factor
- drawdown
- position net PnL

Mixed years such as `2017` and `2023` are intentionally excluded from this first isolation pass.

## Main finding

The first negative-year isolation does **not** support the simple story that the negative annual surface is mainly an early-transition defensive bug.

Instead, all three clearly negative years are dominated by the same broader shape:

- baseline `LONG` entries being converted into router `NO_TRADE`, and
- a smaller but still large second wave of later router `CONTINUATION` entries appearing where the absent path is on `COOLDOWN_ACTIVE`

This means the negative years look more like a recurring **suppression + later continuation displacement** structure than a pure early defensive-transition pocket.

## Evidence summary by year

### 2019

Top action flows:

- `LONG -> NONE`: `513 / 767`
- `NONE -> LONG`: `247 / 767`

Dominant context:

- zone: `low` (`515 / 767`)
- bars-since-regime-change bucket: `8+` (`758 / 767`)
- main blocking reasons: `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence`
- main replacement reason: `stable_continuation_state`

### 2021

Top action flows:

- `LONG -> NONE`: `499 / 702`
- `NONE -> LONG`: `203 / 702`

Dominant context:

- zone: `low` (`505 / 702`)
- bars-since-regime-change bucket: `8+` (`702 / 702`)
- main blocking reasons: `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence`
- main replacement reason: `stable_continuation_state`

### 2024

Top action flows:

- `LONG -> NONE`: `527 / 753`
- `NONE -> LONG`: `222 / 753`

Dominant context:

- zone: `low` (`516 / 753`)
- bars-since-regime-change bucket: `8+` (`736 / 753`)
- main blocking reasons: `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence`
- main replacement reason: `stable_continuation_state`

There are still real early-2024 no-trade / defensive examples in the annual action-diff file, and the frozen annual note cited those correctly as representative examples.
But on the broader aggregate action-diff surface, those early transition rows are **not** the dominant mass of the negative year.

## Cross-year isolation reading

The recurring negative-year pocket shape is:

1. **late low-zone suppression**
   - absent `LONG` becomes enabled `NONE`
   - router resolves mainly to `RI_no_trade_policy`
   - the recurring suppressive reasons are `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence`
2. **later continuation substitution**
   - absent `NONE` becomes enabled `LONG`
   - router resolves mainly to `RI_continuation_policy`
   - the recurring release reason is `stable_continuation_state`

This looks structurally closer to a recurring **phase-shift / displacement** story than to a one-off defensive-transition activation problem.

## What this slice does and does not prove

What this slice supports:

- the negative full years share a real recurring action-diff structure
- that structure is concentrated mainly in `low` zone and overwhelmingly in `bars_since_regime_change >= 8`
- the shared negative-year mass is more about `NO_TRADE` suppression plus later `CONTINUATION` substitution than about a dominant defensive pocket

What this slice does **not** yet prove:

- that the negative-year structure is unique to negative years rather than a router-wide shape that becomes harmful only in some environments
- that the already-documented 2023 seam-A cooldown-displacement diagnosis is the exact same mechanism on `2019`, `2021`, and `2024`
- that any runtime retune is justified

## Consequence

The next honest follow-up should remain read-only and comparative:

1. compare the same pocket summary against clearly positive curated years (`2018`, `2020`, `2022`, `2025`), and
2. only then decide whether the negative years contain a unique harmful pocket or merely a stronger instance of a more general router behavior.

## What is not justified from this slice

- new router tuning
- reopening aged-weak runtime work
- reopening low-zone runtime work
- any claim that one already-known helper family is now proven to explain the whole annual failure surface
