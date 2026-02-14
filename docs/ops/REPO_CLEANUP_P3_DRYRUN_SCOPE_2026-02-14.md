# Repo Cleanup P3 Dry-Run Scope (2026-02-14)

## Syfte

Definiera verifierbar dry-run-scope för kommande cleanup utan att utföra någon flytt/radering.

## Status

Denna scope är **införd** som dokumenterad dry-run-process.

Ingen destruktiv åtgärd är införd i detta steg.

## Input-källor

- `docs/ops/REPO_INVENTORY_REPORT_2026-02-14.md`
- `docs/ops/REPO_RETENTION_POLICY_DRAFT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P2_CONTRACT_2026-02-14.md`

## Kandidatmönster för dry-run

Följande mönster är kandidater för första dry-run-rapportering:

1. `results/hparam_search/**`
2. `results/backtests/*`
3. `scripts/archive/**`
4. `scripts/debug_*.py`
5. `scripts/diagnose_*.py`
6. `scripts/test_*.py`
7. Root-artefakter i kategori C enligt inventory-rapporten

## Exkluderingar (måste kvarstå)

- `src/**`
- `tests/**`
- `config/**`
- `.github/**`
- `registry/**`
- `docs/ops/**` (governance-artefakter)

## Acceptance-checks för kommande destruktiv fas

Följande måste vara uppfyllt innan någon destruktiv commit får påbörjas:

1. Retention policy är beslutad (inte bara draft) med explicit klassning per målområde.
2. Dry-run-rapport publicerad med filantal + paths per mönster.
3. Separat destruktivt commit-kontrakt med tight Scope IN/OUT.
4. Opus pre-code godkännande av den destruktiva fasen.
5. Explicit godkännande från requester före utförande.

## Out of scope i P3

- Ingen faktisk flytt/radering.
- Ingen ändring av build/test/CI-beteende.
- Ingen ändring av runtime/API/config authority paths.
