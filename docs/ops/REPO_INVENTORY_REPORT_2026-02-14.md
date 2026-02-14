# Repo Inventory Report (P1, 2026-02-14)

## Syfte

Icke-destruktiv inventering av repo-strukturen inför fortsatt cleanup. Denna rapport ändrar eller tar inte bort filer.

## Översikt

- Totalt inventerade filer (exkl. tekniska cache-kataloger): **4126**

## Top-level filantal

| Katalog | Antal filer |
| --- | ---: |
| `.bandit` | 1 |
| `.cursor` | 5 |
| `.env` | 1 |
| `.env.example` | 1 |
| `.git-rewrite` | 1 |
| `.gitattributes` | 1 |
| `.github` | 35 |
| `.gitignore` | 1 |
| `.pre-commit-config.yaml` | 1 |
| `.ruff_cache` | 66 |
| `.secrets.baseline` | 1 |
| `.vscode` | 2 |
| `AGENTS.md` | 1 |
| `CHANGELOG.md` | 1 |
| `CLAUDE.md` | 1 |
| `DEV_MARKER.txt` | 1 |
| `README.md` | 1 |
| `archive` | 80 |
| `bandit.yaml` | 1 |
| `burnin_summary.json` | 1 |
| `cache` | 17 |
| `candles.json` | 1 |
| `config` | 256 |
| `conftest.py` | 1 |
| `data` | 22 |
| `dev.overrides.example.json` | 1 |
| `docs` | 221 |
| `logs` | 2 |
| `mcp_server` | 9 |
| `optimizer_phase7b.db` | 1 |
| `optuna_search.db` | 1 |
| `pyproject.toml` | 1 |
| `registry` | 13 |
| `reports` | 10 |
| `requirements.lock` | 1 |
| `results` | 2799 |
| `scripts` | 266 |
| `src` | 118 |
| `tests` | 171 |
| `tmp` | 9 |
| `tools` | 3 |

## Fokuskataloger för cleanup

| Katalog | Antal filer |
| --- | ---: |
| `docs` | 221 |
| `scripts` | 266 |
| `results` | 2799 |
| `archive` | 80 |
| `tmp` | 9 |
| `src` | 118 |
| `tests` | 171 |
| `config` | 256 |

## Root-artefakter (status)

### Kategori A (kärnrepo)

| Fil | Finns |
| --- | --- |
| `.gitattributes` | Ja |
| `.gitignore` | Ja |
| `.pre-commit-config.yaml` | Ja |
| `.secrets.baseline` | Ja |
| `AGENTS.md` | Ja |
| `bandit.yaml` | Ja |
| `CHANGELOG.md` | Ja |
| `CLAUDE.md` | Ja |
| `conftest.py` | Ja |
| `dev.overrides.example.json` | Ja |
| `pyproject.toml` | Ja |
| `README.md` | Ja |

### Kategori B (miljö/operativt lokalt)

| Fil | Finns |
| --- | --- |
| `.env` | Ja |
| `.env.example` | Ja |

### Kategori C (artefakter/scratch-kandidater)

| Fil | Finns |
| --- | --- |
| `burnin_summary.json` | Ja |
| `candles.json` | Ja |
| `DEV_MARKER.txt` | Ja |
| `optimizer_phase7b.db` | Ja |
| `optuna_search.db` | Ja |

## Kandidatmönster (föreslagen uppföljning)

| Mönster | Matchade filer |
| --- | ---: |
| `docs/daily_summaries/*.md` | 34 |
| `results/backtests/*` | 264 |
| `results/hparam_search/**` | 2416 |
| `scripts/archive/**` | 59 |
| `scripts/debug_*.py` | 10 |
| `scripts/diagnose_*.py` | 8 |
| `scripts/test_*.py` | 20 |

## Notering

Rensning/flytt/radering är fortsatt **föreslagen** och kräver separat kontrakt i senare etapp (P2/P3).
