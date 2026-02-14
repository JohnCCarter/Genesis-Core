# Repo Cleanup P3 Dry-Run Report (2026-02-14)

## Syfte

Dokumentera verifierbar dry-run-output för kandidatområden inför en framtida,
separat godkänd destruktiv cleanup-fas.

## Status

Denna rapport är **införd** som icke-destruktiv mätning.

Ingen flytt eller radering har utförts i detta steg.

## Mätmetod

- Endast read-only uppräkning av filer per kandidatmönster.
- Ingen filmodifiering i målområden (`results/**`, `scripts/**`, root-artefakter).

## Kandidatmönster — uppmätta antal

| Mönster | Antal filer |
| --- | ---: |
| `results/hparam_search/**` | 2416 |
| `results/backtests/*` | 264 |
| `scripts/archive/**` | 59 |
| `scripts/debug_*.py` | 10 |
| `scripts/diagnose_*.py` | 8 |
| `scripts/test_*.py` | 20 |

## Root-kandidater (kategori C) — existens

| Fil | Finns |
| --- | --- |
| `burnin_summary.json` | Ja |
| `candles.json` | Ja |
| `DEV_MARKER.txt` | Ja |
| `optimizer_phase7b.db` | Ja |
| `optuna_search.db` | Ja |

## Slutsats

- Dry-run-scope är mätbar och reproducerbar på aktuell branchstate.
- Nästa steg (destruktiv fas) är fortsatt **föreslagen** och kräver:
  1. separat destruktivt commit-kontrakt,
  2. Opus pre-code godkännande,
  3. explicit godkännande från requester.
