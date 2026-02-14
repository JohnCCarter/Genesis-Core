# Repo Cleanup D2 Hardening Contract (2026-02-14)

## Category

`tooling`

## Scope IN

- `scripts/parse_burnin_log.py`
- `docs/ops/REPO_CLEANUP_D2_HARDEN_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D2_HARDEN_REPORT_2026-02-14.md`
- `AGENTS.md`

## Scope OUT

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `results/**`
- `tmp/**`

## Constraints

Default: `NO BEHAVIOR CHANGE`

- Explicit behavior-change exception gäller endast output-path i
  `scripts/parse_burnin_log.py`.
- Parsinglogik och JSON-innehåll ska vara oförändrade.
- Ingen ändring av runtime/API/config authority paths.

## Done criteria

1. `parse_burnin_log.py` skriver default-output till archive-path:
   `archive/_orphaned/root_artifacts/2026-02-14/burnin_summary.json`.
2. Scriptet skapar parent-katalog vid behov.
3. Ingen default-skrivning till root `burnin_summary.json`.
4. Opus post-code diff-audit godkänd.

## Gates

1. Scope gate: endast Scope IN-filer ändrade.
2. Script gate: output-path verifierad till archive-path.
3. No-drift gate: parsinglogik oförändrad.
4. Opus diff-audit: APPROVED.

## Status

- D2-hardening i detta kontrakt är införd när commit är verifierad.
