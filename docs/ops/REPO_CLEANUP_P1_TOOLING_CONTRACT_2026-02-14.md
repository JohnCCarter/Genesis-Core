# Repo Cleanup P1 Tooling Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/repo_inventory_report.py`
- `docs/ops/REPO_CLEANUP_P1_TOOLING_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_INVENTORY_REPORT_2026-02-14.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/runtime*.json`
- `results/**`
- `archive/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Inga ändringar i runtime-logik, defaults, seeds eller API-kontrakt.
- Scriptet är read-only mot repo-innehåll och får endast skriva rapport till:
  - `docs/ops/REPO_INVENTORY_REPORT_2026-02-14.md`
- Inga flyttar/raderingar i P1.

## Done criteria

1. Inventory-script finns och körs utan fel.
2. Rapport genereras med stabil sortering och tydliga sektioner.
3. Endast Scope IN-filer påverkas.
4. Opus diff-audit godkänd.

## Gates

1. `black --check scripts/repo_inventory_report.py`
2. `ruff check scripts/repo_inventory_report.py`
3. `python scripts/repo_inventory_report.py`
4. Scope gate + Opus diff-audit

## Statusdisciplin

- Policy för senare rensning markeras som `föreslagen` tills separat implementation är verifierad.
- Inga påståenden om `införd` destruktiv städning i P1.
