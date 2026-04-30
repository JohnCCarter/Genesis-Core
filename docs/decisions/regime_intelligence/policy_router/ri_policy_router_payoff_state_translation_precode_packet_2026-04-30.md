# RI policy router payoff-state translation pre-code packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `pre-code-defined / docs-only / RI chosen / no implementation or execution authority`

This packet translates the root research note `genesis_core_router_research.md` into a
Genesis-compatible RI lane.

It freezes one explicit direction choice:

- future structural router work should target **RI first**, not `Legacy`

It also freezes one explicit architectural translation:

- **payoff-state** is the intended research/evaluation truth,
- while **RI decision-time state** remains the admissible first runtime carrier.

This packet does **not** authorize runtime changes, execution, schema widening, family-rule
changes, Legacy implementation, cross-family routing, exit rewrites, or promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only and freezes one Genesis-specific translation of a research note into the existing RI family-local lane without touching runtime/config/test/results surfaces.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the user has chosen RI rather than Legacy as the future implementation surface, but the research note still needs a Genesis-specific translation before any high-sensitivity runtime packet is proposed.
- **Objective:** define how the payoff-state research note maps onto Genesis-Core, preserving RI as the primary implementation surface, Legacy as a later control line only, and decision-time-only RI state as the first runtime carrier.
- **Candidate:** `RI payoff-state translation`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

### Concept lane

- **Hypotes / idé:** Genesis should treat payoff-state as the research/evaluation SSOT for what the router is really trying to detect, while the existing RI family-local decision-time router remains the first admissible runtime carrier for implementation.
- **Varför det kan vara bättre:** the research note directly matches the observed inversion shape (defensive logic often helps weak years but hurts good years), and Genesis already has a bounded default-off RI-local router surface with state, dwell, hysteresis, and size-only defensiveness that can host a first structural improvement without widening into Legacy or cross-family routing.
- **Vad skulle falsifiera idén:** if later RI evidence shows that decision-time RI proxies cannot approximate payoff-favorable vs payoff-harmful pockets better than the current router state, or if the dominant mechanism turns out to be an exit-side or cross-family effect that cannot be expressed honestly inside the RI-local lane.
- **Billigaste tillåtna ytor:** `docs/decisions/regime_intelligence/policy_router/**`, `docs/analysis/regime_intelligence/policy_router/**`, existing read-only RI evidence roots, and repo-visible RI runtime seams already bounded by earlier packets.
- **Nästa bounded evidence-steg:** one RI-only future packet that keeps decision-time-only inputs, preserves size-first defensiveness, and scopes the smallest admissible structural runtime change — most likely asymmetric defensive activation/release semantics in `src/core/strategy/ri_policy_router.py` with explicit config-authority support only if truly required.

### Constraints

- `docs-only`
- `concept-only / translation-only / non-authorizing`
- `RI is the primary future implementation surface`
- `Legacy may be used later as a control/comparator only`
- `No payoff/outcome fields admitted to runtime from this packet`
- `No cross-family routing`
- `No exit-side rewrite`
- `No adaptive runtime behavior or online learning`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this slice is docs-only and does not execute a runtime, backtest, or implementation workflow.
- **Reserved for any later code slice:** `python_engineering`, `decision_gate_debug`, `config_authority_lifecycle_check`
- **Deferred to any later runnable evidence step:** `backtest_run`, `genesis_backtest_verify`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

## Why this packet exists now

The user has now explicitly chosen the RI lane rather than the Legacy lane for future structural
router work.

Current repo-visible evidence also makes that choice the cleaner implementation target:

1. `docs/scpe_ri_v1_architecture.md` already defines the architecture lane as **RI-only** and explicitly keeps `Legacy` out of routing scope
2. `src/core/strategy/ri_policy_router.py` already exists as a bounded default-off RI family-local router with explicit state, dwell, hysteresis, and size-multiplier posture handling
3. `src/core/strategy/decision.py` already integrates that RI router on the decision-time path before sizing
4. the Legacy annual sweep is useful as control evidence, but it does not reopen Legacy as the right first implementation surface
5. the root research note correctly argues that the real target is payoff-shape detection, but that does not automatically make post-trade payoff fields admissible as runtime inputs under the current RI V1 decision-time contract

## Evidence anchors

- `genesis_core_router_research.md`
- `docs/scpe_ri_v1_architecture.md`
- `src/core/strategy/ri_policy_router.py`
- `src/core/strategy/decision.py`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/legacy/policy_router/legacy_policy_router_enabled_vs_absent_all_years_execution_summary_2026-04-30.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
- `GENESIS_WORKING_CONTRACT.md`

## Exact translation contract

### 1. Payoff-state is the research/evaluation truth, not the first runtime input

This packet preserves the following translation from the research note:

- what the system **really** wants to know is payoff-state
- but the first runtime implementation must still respect Genesis decision-time validity rules

So in Genesis terms:

- payoff-state is the target semantics for research/evaluation
- decision-time RI state is the admissible runtime carrier

This means the note is adopted as a **design target**, not as literal immediate runtime input authority.

### 2. Current RI runtime carrier remains decision-time-only

Per `docs/scpe_ri_v1_architecture.md`, current RI routing remains bounded to decision-time-valid
fields.

That means the following stay out of runtime scope for now:

- `mfe_*`
- `mae_*`
- `fwd_*`
- direct post-trade expectancy fields
- any payoff/outcome-derived field whose decision-time validity is not proven

Those may still be used later on research/evidence surfaces to label or evaluate pockets, but not as
first-step runtime inputs from this packet.

### 3. RI is the implementation surface; Legacy is the control line

This packet freezes the following role split:

- **RI** = primary implementation surface for future structural router work
- **Legacy** = later control/comparison surface only

The Legacy annual sweep already shows that the leaf is materially active inside a true Legacy carrier,
but that does not make Legacy the preferred architecture lane.

### 4. Size-first defensiveness is admissible earlier than exit-side defensiveness

Current RI router integration already expresses defensiveness through:

- `RI_no_trade_policy`, or
- a `defensive_size_multiplier`

That means the research note's convexity-preserving idea is translated here as:

- size-first defensiveness is an admissible near-term RI direction
- exit-side switching, bumpless transfer across open positions, or controller reset semantics remain later, wider questions and are not the first implementation target from this packet

### 5. Shadow / payoff diagnostics belong to research first

The research note's strongest payoff-state ideas are preserved here first as offline truth /
research-evidence surfaces, for example:

- expectancy slope
- MFE/MAE asymmetry
- R-multiple skew
- AR(1) / variance on outcomes
- shadow/witness policy comparison

Those ideas are treated here as:

- valid research/evaluation targets
- possible later evidence-labeling tools
- not yet automatic runtime dependencies

## What fits Genesis now vs later

### Admissible early RI implementation directions

The following are compatible with the current RI lane and are reasonable future runtime candidates,
subject to a separate implementation packet and review:

- asymmetric defensive activation / release semantics
- richer policy-conditional router state
- do-no-harm bias toward continuation / base posture
- explicit size-first defensive posture refinement
- clearer detector-state vs policy-state separation inside the RI router

### Requires wider architecture or later runtime authority

The following do **not** belong to the first RI implementation step from this packet:

- direct runtime use of payoff/outcome fields
- cross-family RI-vs-Legacy routing
- exit-side switching as the primary first mechanism
- bumpless transfer / open-position controller carry-over
- broader meta-strategy runtime selection across families

### Best treated as research/evidence first

The following should first be used to judge or label router quality on research surfaces:

- payoff-shape regime definitions
- offline discriminative state labeling
- witness/shadow policy dominance checks
- do-no-harm threshold calibration from historical harmful pockets

## Exact next admissible step preserved by this packet

If the user wants to continue immediately on the RI line after this packet, the smallest admissible
next move is:

- one **RI-only future runtime pre-code packet** for a bounded structural change rooted in `src/core/strategy/ri_policy_router.py`
- keeping the current decision-time-only state contract intact
- keeping `Legacy` out of implementation scope
- keeping defensive behavior size-first rather than exit-first
- adding config-authority/schema support only if the new structural semantics truly require explicit new leaf fields

Preferred first candidate question:

> Can Genesis improve the RI router by making defensive activation/release asymmetric and more explicitly biased toward continuation, while preserving decision-time-only state, default-off parity, and size-first defensiveness?

This packet preserves that as the most honest next RI-facing code question.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - explicit citation to the root research note and current RI/Legacy anchors only
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - `tmp/**`
  - runtime execution
  - schema/config changes
  - Legacy implementation
  - cross-family routing
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/regime_intelligence/policy_router/ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens
no executable surface by itself.

## Stop Conditions

- the packet starts implying that payoff/outcome fields are already admitted to the RI runtime path
- the packet starts reopening Legacy as the primary implementation surface
- the packet widens into cross-family routing, exit rewrites, or runtime-authority language
- the next follow-up can no longer stay inside a bounded RI-local lane
- any need to modify files outside the two scoped docs files

## Output required

- one Genesis-specific RI translation packet for the payoff-state research note
- one updated working anchor

## Bottom line

The research note is adopted here as a structural target for Genesis, but not as literal runtime
permission to consume payoff fields directly. The correct translation is:

- payoff-state is the **research/evaluation truth**,
- RI decision-time state is the **first runtime carrier**,
- RI is the **implementation surface**,
- Legacy remains the **control/comparison line** only.

This packet preserves that boundary and freezes the next honest RI-facing question without opening
implementation authority by itself.
