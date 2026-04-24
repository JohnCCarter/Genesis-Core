# RI policy router continuation split seam direction packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / concept-lane direction freeze / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice constrains future candidate authoring around a verified split seam, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Concept` — why this is the cheapest admissible lane now: the fail-set and seam replay evidence already exist, and the next honest need is to freeze what the evidence now means before any new runtime candidate is authored.
- **Objective:** preserve the verified split-seam interpretation so the next candidate must explicitly choose whether it targets weak pre-aged continuation or already-strong continuation, instead of treating the late-December seam as one homogeneous phenomenon.
- **Candidate:** `post-failset split seam framing`
- **Base SHA:** `HEAD`

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: this slice exists to prevent blind retuning by preserving the verified gate/state-level interpretation of the failing rows.
- **Conditional repo-local spec:** `python_engineering`
  - reason: any follow-up runtime candidate must still remain small, typed, and test-backed, but this docs-only packet does not itself modify code.

### Concept lane

- **Hypotes / idé:**
  - the observed late-December failure is not one seam but at least two distinct continuation-local seams.
  - `2023-12-22T15:00:00+00:00` is a `weak continuation but not aged enough` case.
  - `2023-12-24T21:00:00+00:00` is an `already strong continuation` case.
- **Varför det kan vara bättre:**
  - it prevents the next slice from overloading one candidate with incompatible targets.
  - it keeps future runtime changes falsifiable and continuation-local.
  - it makes escalation conditions explicit if the next candidate wants to touch strong continuation semantics.
- **Vad skulle falsifiera idén:**
  - a bounded read-only replay or new deterministic evidence proves that both target rows can be removed by one single continuation-local predicate without touching stable continuation semantics.
  - the supposedly strong row reclassifies under the relevant frozen surface and no longer lands in `stable_continuation_state` / `mandate_level = 3`.
- **Billigaste tillåtna ytor:**
  - `docs/governance/**`
  - existing fail-set evidence docs
  - existing decision-row artifacts
  - read-only replay / trace analysis
- **Nästa bounded evidence-steg:**
  - author one fresh candidate packet that explicitly names only one target seam class.
  - if the next candidate aims at `already strong continuation`, reopen governance review before any runtime edit because that no longer fits the old weak-continuation-only assumption.

## Verified split-seam facts

### Seam A — weak continuation before the current age gate

Observed on `2023-12-22T15:00:00+00:00`:

- `bars_since_regime_change = 7`
- `switch_reason = continuation_state_supported`
- `mandate_level = 2`
- `previous_policy = RI_no_trade_policy`

Interpretation:

- this row belongs to the weak-continuation seam,
- but it is not reachable by the current `>= 16` aged guard.

### Seam B — already strong continuation

Observed on `2023-12-24T21:00:00+00:00`:

- `bars_since_regime_change = 13`
- `switch_reason = stable_continuation_state`
- `mandate_level = 3`
- `previous_policy = RI_continuation_policy`
- `switch_proposed = false`

Interpretation:

- this row is already in strong/stable continuation,
- so any candidate that wants to remove it is no longer a pure weak-continuation admission guard.

### Actual guard-hit seam

Observed on `2023-12-28T06:00:00+00:00` and `2023-12-30T18:00:00+00:00`:

- late regime age (`19`, `22`)
- below strong confidence
- below strong edge
- `switch_reason = AGED_WEAK_CONTINUATION_GUARD`

Interpretation:

- the implemented guard is functioning on its own declared seam,
- but that seam is not identical to the originally targeted losing pair.

## Direction lock for future candidate authoring

Future packets must not describe the late-December continuation issue as one single seam without qualification.

Any next candidate must explicitly declare one of the following targets:

1. **Weak-pre-aged continuation seam**
   - continuation-local
   - should remain below strong-continuation semantics
   - may stay within a weak-continuation admission framing if it can be expressed tightly

2. **Already-strong continuation seam**
   - touches stable continuation semantics or continuation carry behavior
   - is more behavior-sensitive than the first candidate
   - must not be bundled into the old `aged weak continuation guard` framing

## Governance implication

The previous candidate contract assumed the next runtime slice could remain a weak-continuation-only intervention.

That remains valid only for seam class `1` above.

If the next candidate needs to affect seam class `2`, the work must be re-packeted honestly as a broader continuation-semantics question before any runtime edit begins.

## Scope

- **Scope IN:**
  - `docs/governance/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `registry/**`
  - any runtime/default/champion/promotion/family-rule surface
- **Expected changed files:**
  - `docs/governance/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal docs validation on the changed files

## Stop Conditions

- the next packet tries to target both seam classes while still claiming weak-continuation-only scope
- the next candidate implicitly changes strong continuation semantics without saying so
- the next step drifts into `DEFENSIVE`, sizing, exits, family-rule, or authority surfaces

## Output required

- one repo-visible split-seam direction freeze
- one updated working anchor that forces explicit seam selection before any next runtime candidate is authored
