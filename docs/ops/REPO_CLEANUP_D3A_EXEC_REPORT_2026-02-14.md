# Repo Cleanup D3A Execution Report (2026-02-14)

## Syfte

Genomföra första kandidatvisa D3-flytten med lägsta möjliga referensrisk.

## Flyttade script (move-only)

1. `scripts/debug_config_merge.py`
2. `scripts/debug_decision_pipeline.py`
3. `scripts/debug_htf_loading.py`
4. `scripts/debug_model_bias.py`
5. `scripts/debug_param_transforms.py`
6. `scripts/debug_swing_detection.py`

Ny path för samtliga:

- `scripts/archive/debug/2026-02-14/`

## Exkluderade script i D3A (refererade)

- `scripts/debug_htf_exit_usage.py`
- `scripts/debug_mcp_tunnel.py`
- `scripts/debug_strategy_signals.py`

Dessa hanteras i senare kandidatvisa kontrakt.

## Verifiering

- Scope gate: endast kontrakterade paths i diff.
- Rename-diff verifierad för samtliga 6 flyttar.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3A är införd som move-only för 6 lågkopplade debug-script.
- Övrigt D3-scope är fortsatt föreslaget och kandidatvis.
