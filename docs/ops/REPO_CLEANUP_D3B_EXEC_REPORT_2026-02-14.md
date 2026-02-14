# Repo Cleanup D3B Execution Report (2026-02-14)

## Syfte

Genomföra nästa kandidatvisa D3-flytt för återstående debug-script med kända docs-referenser.

## Flyttade script (move-only)

1. `scripts/debug_htf_exit_usage.py`
2. `scripts/debug_mcp_tunnel.py`
3. `scripts/debug_strategy_signals.py`

Ny path för samtliga:

- `scripts/archive/debug/2026-02-14/`

## Känd referenspåverkan (dokumenterad)

Historiska docs/changelog refererar gamla script-paths och uppdateras inte i D3B:

- `CHANGELOG.md` (mcp_tunnel, htf_exit_usage)
- `docs/fibonacci/*` (htf_exit_usage, strategy_signals)
- `docs/archive/COMMIT_MSG_HTF_EXITS.txt`

## Operativ notering

- Flytten är move-only utan innehållsändring i scripten.
- Två av scripten innehåller egna usage/path-antaganden baserade på tidigare path.
  Detta dokumenterar referensdrift men gör ingen kodjustering i D3B.

## Verifiering

- Scope gate: endast kontrakterade filer i diff.
- Rename-diff verifierad för samtliga 3 flyttar.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D3B är införd som move-only för 3 refererade debug-script.
- D3 övergripande scope är fortsatt föreslaget kandidatvis för övriga mönster.
