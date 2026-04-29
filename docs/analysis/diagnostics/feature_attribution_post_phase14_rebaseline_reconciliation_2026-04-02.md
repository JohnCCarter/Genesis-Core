# Feature Attribution — post-Phase-14 rebaseline reconciliation

Date: 2026-04-02
Mode: `RESEARCH`
Base SHA anchor: `b7a6a7de`
Branch: `feature/ri-role-map-implementation-2026-03-24`

## 1. Purpose and boundary

This memo is the restart bridge between the already completed Feature Attribution v1 synthesis and the later Phase 14 edge-origin conclusion.

It is **observational only**.
It does not authorize execution, reruns, promotion, readiness, or runtime changes.
It does not reinterpret earlier FA-v1 artifacts as if they automatically validated the current executable route.

Its only job is to separate the two live reference surfaces cleanly and record the first replay-candidate ordering for future governed review.

## 2. Frozen historical baseline

The frozen historical baseline remains the reference surface used by the earlier FA-v1 slice artifacts.

Locked historical baseline metrics:

- `total_return_pct = 1.6508216023`
- `profit_factor = 2.1454408663`
- `max_drawdown = 1.3087994631`
- `trade_count = 146`
- `win_rate = 76.0273972603`

This surface remains valid as **historical FA-v1 provenance**.
It must not be silently reused as if it were the currently reproduced executable-route baseline on this branch.

## 3. Current executable-route baseline

The FA-v1 synthesis also records a different current executable-route baseline on this branch.

Current executable-route baseline metrics:

- `total_return_pct = 1.2608648188`
- `profit_factor = 2.3190143283`
- `max_drawdown = 1.4411992822`
- `trade_count = 82`
- `win_rate = 74.3902439024`

This is the correct baseline surface for any plain-language question of the form:

> what is most active on the route that is executable now?

## 4. Baseline drift summary

The two surfaces no longer match and must not be conflated.

Current executable route versus frozen historical baseline:

| Metric             | Frozen historical baseline | Current executable route |           Drift |
| ------------------ | -------------------------: | -----------------------: | --------------: |
| `total_return_pct` |             `1.6508216023` |           `1.2608648188` | `-0.3899567835` |
| `profit_factor`    |             `2.1454408663` |           `2.3190143283` | `+0.1735734620` |
| `max_drawdown`     |             `1.3087994631` |           `1.4411992822` | `+0.1323998191` |
| `trade_count`      |                      `146` |                     `82` |           `-64` |
| `win_rate`         |            `76.0273972603` |          `74.3902439024` | `-1.6371533579` |

Practical reading:

- the current route is **not** a reproduction of the frozen FA-v1 route
- historical slice labels remain historically meaningful, but they are not enough by themselves for current-route prioritization
- restart prioritization therefore has to key off current-route marginal evidence rather than older frozen-slice labels alone

## 5. Current-route activity ranking

The current executable-route ranking by absolute `total_return_pct` delta is:

1. `Volatility sizing cluster` — `+0.9196103062`
2. `Regime sizing multiplier cluster` — `+0.6588756573`
3. `Signal-adaptation threshold cluster` — `+0.3948827769`
4. `HTF regime sizing multiplier cluster` — `+0.3152162047`
5. `Minimum-edge gate seam` — `0.0`
6. `Hysteresis gate seam` — `0.0`
7. `Cooldown gate seam` — `0.0`
8. `HTF block seam` — `0.0`
9. `LTF override cluster` — `0.0`

Observational-only interpretation of the active end of the ranking:

- `Volatility sizing cluster` is the strongest live mover on the current route, but remains a trade-off surface because neutralization improved upside and PF while worsening DD
- `Regime sizing multiplier cluster` is also clearly live, but likewise remains mixed rather than cleanly positive or negative
- `Signal-adaptation threshold cluster` is the clearest current-route harmful surface in plain-language terms
- `HTF regime sizing multiplier cluster` is active but less decisive than the three surfaces above

This ranking is observational only.
It does not authorize execution, reruns, promotion, readiness, or runtime changes.

## 6. Restart interpretation under Phase 14

Phase 14 does not say that single admitted units are irrelevant.
It says that, within the packet-authorized artifact surface, the best-supported broader origin hypothesis remains `emergent_system_behavior`.

That means the restart lane should interpret FA-v1 this way:

- current-route cluster activity can still matter
- but no current admitted unit should be treated as already disproving the broader system-level interpretation
- replay priority should be driven by current-route salience and interpretability, not by an assumption that one cluster is already the complete mechanism

Portable post-Phase-14 takeaways from the existing FA-v1 synthesis are therefore:

- the route split itself is real and must be carried forward explicitly
- no admitted unit is currently a robust standalone edge-driver on the executable route
- `Volatility sizing cluster` is the strongest current-route mover
- `Signal-adaptation threshold cluster` is the clearest current-route harmful surface
- several other admitted seams are currently inert on the executable route

## 7. Locked next-candidate order

The recorded replay-candidate order for future governed review is:

1. `Volatility sizing cluster`
2. `Signal-adaptation threshold cluster`
3. admitted sizing interaction ladder

Why this order:

- `Volatility sizing cluster` is first because it is both highly active and structurally interpretable on the current route
- `Signal-adaptation threshold cluster` is second because it is the clearest harmful current-route surface and has direct threshold-ownership significance
- the broader sizing interaction ladder comes after those two because multiplicative confounding should be revisited only after the strongest single current-route mover is re-examined first

This memo records the first replay-candidate ordering for future governed review only.
It does not authorize execution, reruns, promotion, readiness, or runtime changes.

## 8. Bottom line

Feature Attribution restart work should proceed from a simple rule:

> use the frozen historical FA-v1 baseline as provenance, use the current executable-route baseline as the live prioritization surface, and start the replay lane with `Volatility sizing cluster` under the still-active Phase 14 `emergent_system_behavior` frame.

That is the cleanest post-Phase-14 restart boundary supported by the currently locked evidence.
