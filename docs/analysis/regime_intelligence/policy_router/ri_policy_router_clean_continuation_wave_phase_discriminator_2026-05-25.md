# RI policy router clean continuation wave phase discriminator

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Status: `completed / read-only clean-continuation wave discriminator / observational only`

This slice stays inside the current `clean_continuation` state label.
It does **not** widen policy identities and it does **not** reinterpret `wave 2` as blocked or defensive.

The question is narrower:

> inside the already-locked `clean_continuation` state, can `wave 1` and `wave 2` be separated by any simple decision-time-only discriminator?

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/research-next-bounded-case-2026-05-25`
- **Risk:** `LOW` — read-only deterministic discriminator pass over an already-generated fixed-subject taxonomy artifact
- **Required Path:** `Quick`
- **Lane:** `Research-evidence`
- **Objective:** test whether the two fixed `2023-12` clean-continuation waves can be separated by a simple decision-time-only discriminator without collapsing the state/policy separation or touching runtime behavior
- **Candidate:** `clean continuation wave phase discriminator`
- **Base SHA:** `270b65346ebe9208c953abfc7181bf83df34d8f5`

## Scope

### Scope IN

- one read-only wave discriminator helper
- one JSON artifact over the already-generated fixed-subject taxonomy artifact
- one short evidence note describing which decision-time features do and do not separate the two clean-continuation waves

### Scope OUT

- `src/**`
- `tests/**`
- runtime routing changes
- new policy identities
- threshold retuning
- year widening
- promotion/readiness claims

## Evidence inputs

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_12_vs_2024_fixed_window_phase_contrast_2026-05-25.md`
- `results/evaluation/ri_policy_router_fixed_subject_state_taxonomy_pass_2026-05-25.json`
- `results/evaluation/ri_policy_router_clean_continuation_wave_phase_discriminator_2026-05-25.json`
- `scripts/analyze/ri_policy_router_clean_continuation_wave_phase_discriminator_20260525.py`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_clean_continuation_wave_phase_discriminator_20260525.py --base-sha 270b65346ebe9208c953abfc7181bf83df34d8f5`

## Main result

Yes — but only one simple decision-time feature separates the two fixed clean-continuation waves perfectly on this carrier:

- `bars_since_regime_change`

Perfect single-feature rules found:

- `bars_since_regime_change <= 369` -> `wave 1`
- `bars_since_regime_change >= 369` -> `wave 2`

No other tested single feature achieved perfect separation:

- `action_edge`
- `confidence_gate`
- `clarity_score`

So the best current bounded reading is:

> the internal split inside `clean_continuation` is presently a **phase-age discriminator first**, not a clean confidence/clarity/edge discriminator.

## Observed

### 1. Both waves remain the same state class

The source taxonomy artifact already locked both subjects as `clean_continuation`.
That remained true here.

Both waves still share the same decision-time qualitative shell:

- `phase_label = continuation_release`
- `selected_policy = RI_continuation_policy`
- `switch_reason = stable_continuation_state`
- `zone = low`

So this slice does **not** support relabeling `wave 2` as blocked, defensive, or no-trade.

### 2. `bars_since_regime_change` cleanly separates the two fixed waves

Observed ranges:

- `wave 1`: `363` -> `368`
- `wave 2`: `370` -> `378`

This gives a clean no-overlap interval between the waves:

- lower exclusive bound: `368`
- upper exclusive bound: `370`

That is why a simple threshold at `369` separates the two fixed waves perfectly on this carrier.

### 3. Policy-local scores weaken on `wave 2`, but they do not separate cleanly by themselves

Decision-time feature gaps, `wave 2` minus `wave 1`:

- `action_edge`: `-0.013692`
- `confidence_gate`: `-0.006846`
- `clarity_score`: `-0.714286`

Those are directionally consistent with weakening, but their ranges still overlap.

Best single-feature rules among the overlapping metrics:

- `action_edge <= 0.088612` -> `wave 2`
  - accuracy: `0.769231`
  - precision: `1.0`
  - recall: `0.571429`
- `confidence_gate <= 0.544306` -> `wave 2`
  - accuracy: `0.769231`
  - precision: `1.0`
  - recall: `0.571429`
- `clarity_score <= 39.0` -> `wave 2`
  - accuracy: `0.692308`
  - precision: `1.0`
  - recall: `0.428571`

So the weakening is real, but it is not yet a full single-feature state split on those scores alone.

### 4. The later wave is observationally worse on the first proxy surface

Outcome metrics were observational only in this slice.
They were not used in rule search.

Observed `wave 2` minus `wave 1` outcome gaps:

- `fwd_16` mean gap: `-0.872860%`
- `mfe_16` mean gap: `-1.412794%`
- `fwd_16 > 0` share:
  - `wave 1 = 50%`
  - `wave 2 = 0%`

So the observational outcome weakness remains aligned with the phase-age split.

### 5. The categorical shell does not provide a new split

The two waves share the same label set for the main categorical descriptors:

- `zone`
- `selected_policy`
- `switch_reason`
- `phase_label`

`previous_policy` differs only slightly in counts:

- `wave 1`: `RI_no_trade_policy = 1`
- `wave 2`: `RI_no_trade_policy = 2`

That is not a strong enough bounded result to treat prior-policy mix as the main discriminator here.

## Inferred

The cheapest honest next interpretation is now sharper:

> inside the current `clean_continuation` state, the meaningful internal split is a **phase-age / regime-age distinction** before it is a pure confidence, clarity, or edge distinction.

That means the likely next state-language refinement is **not** a brand-new policy.
It is a more explicit sub-reading inside continuation, for example:

- earlier clean continuation, versus
- later clean continuation

with the warning that both still remain inside the same broad clean-continuation state on this carrier.

## Unverified

This slice does **not** prove:

- that `bars_since_regime_change` is a portable separator outside this exact fixed carrier
- that `wave 2` should become a different runtime state label now
- that the overlapping confidence / clarity / edge signals are useless
- that one age-based runtime rule is justified
- that runtime tuning is admissible yet

## What changed and what did not

What changed:

- the repo now has a reproducible wave-one vs wave-two discriminator helper
- the repo now has explicit evidence that the fixed clean-continuation split is presently age-first on this carrier
- the next slice can now talk about a possible continuation phase dimension without confusing it with a new policy identity

What did **not** change:

- no runtime/config/strategy/backtest behavior changed
- no new policy identity was introduced
- no thresholds, guards, or sizing rules changed
- no annual verdict was reopened
- no readiness or promotion claim was made
