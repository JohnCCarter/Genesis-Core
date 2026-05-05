# RI policy router re-anchor after aged-weak closeouts

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / re-anchor complete / no active RI-router runtime packet`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice is docs-only and records the current truthful chain state after already completed positive and negative closeouts without reopening runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the recent runtime slices have already resolved their verdicts, so the honest next step is to re-anchor the chain state before any further candidate framing or lane switch.
- **Objective:** re-anchor the RI-router runtime chain after the positive bars-7 closeout and the negative aged-weak closeouts, and decide whether any active next runtime packet remains admissible on current evidence.
- **Base SHA:** `09e21451`

## Evidence anchors

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_plus_stability_interaction_runtime_packet_2026-04-27.md`
- `GENESIS_WORKING_CONTRACT.md`

## Re-anchor verdict

The RI-router runtime chain is now re-anchored to a **parked** state.

Meaning:

- the retained positive runtime result in this chain remains the bounded `bars-7 continuation-persistence` slice only
- the low-zone bars-8 family is closed negative / reverted
- the aged-weak second-hit runtime slice is closed negative / reverted
- the aged-weak plus stability interaction runtime slice is closed negative / reverted
- there is currently **no active RI-router runtime packet** that is admissible on the present evidence set

## Why the chain is parked

### 1. The remaining aged-weak surface no longer supports the earlier residual-row story

The aged-weak plus stability closeout established that the governed residual-row assumption itself is no longer trustworthy on the active carrier:

- expected direct helper-hit set: `{2023-12-28T09:00:00+00:00, 2023-12-30T21:00:00+00:00}`
- actual direct helper-hit set: `{2023-12-28T09:00:00+00:00, 2023-12-31T00:00:00+00:00}`

So a future candidate cannot honestly reuse the earlier `2023-12-30T21:00:00+00:00` residual-row premise without a fresh re-packeted evidence basis.

### 2. The earlier seam-A chain has already yielded its bounded answer

The single-veto seam-A work removed the repeated same-pocket de-chaining problem and narrowed the fail-set, but the residual diagnosis proved the remaining rows split across distinct mechanisms rather than one unresolved seam-A pocket.

That means there is no honest “just one more seam-A tweak” move left on the current evidence.

### 3. The current positive slice is already isolated and retained

The bars-7 continuation-persistence helper passed its exact helper-hit proof and remains the last retained positive runtime addition in this chain.

That positive result does not authorize widening into fresh runtime work on the now-falsified aged-weak surfaces.

## Consequence

Until new evidence exists, treat the RI-router runtime tuning chain as:

- **runtime parked**
- **no active candidate under implementation**
- **no active Optuna follow-up**
- **no admissible keep-set or stress-set expansion for the falsified aged-weak family**

## Next admissible move

If this chain is reopened at all, the next step must be one of the following:

1. a **fresh docs-only candidate-framing / evidence packet** that is explicitly anchored to the active carrier truth and does not reuse any already-falsified aged-weak residual assumption, or
2. a decision to leave the RI-router chain parked and move attention to another research lane

What is **not** admissible from this re-anchor alone:

- another runtime packet that implicitly continues the aged-weak family
- an Optuna slice on top of the current unresolved/falsified aged-weak story
- reopening seam-A, low-zone bars-8, or aged-weak second-hit semantics without a new evidence anchor

## Output of this slice

- one docs-only re-anchor that records the current truthful RI-router chain state
- one explicit statement that the chain has no active admissible runtime packet on current evidence
- one clear handoff rule: future reopening requires fresh docs-only evidence first
