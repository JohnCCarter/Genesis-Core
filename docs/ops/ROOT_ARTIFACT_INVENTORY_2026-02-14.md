# Root Artifact Inventory (2026-02-14)

## Syfte

Icke-destruktiv inventering av filer i repo-roten för cleanup P0.

## Klassificering

### Kategori A — Kärnrepo (behåll i root)

- `.gitattributes`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.secrets.baseline`
- `AGENTS.md`
- `bandit.yaml`
- `CHANGELOG.md`
- `CLAUDE.md`
- `conftest.py`
- `dev.overrides.example.json`
- `pyproject.toml`
- `README.md`

### Kategori B — Miljö/operativt lokalt (hanteras varsamt)

- `.env` (ska ej committas)
- `.env.example` (template; håll synkad men utan hemligheter)

### Kategori C — Artefakter/scratch-kandidater (föreslagen uppföljning)

- `burnin_summary.json`
- `candles.json`
- `DEV_MARKER.txt`
- `optimizer_phase7b.db`
- `optuna_search.db`

## Rekommenderad åtgärd (föreslagen)

1. Behåll Kategori A i root.
2. Kategori B: säkra att endast `.env.example` versionshanteras.
3. Kategori C: klassificera per fil till någon av:
   - permanent testfixture/data
   - flytt till `reports/` eller `archive/`
   - lokal, ej versionshanterad artefakt

## Guardrails

- Ingen flytt/radering av Kategori C i P0.
- Ingen ändring av runtime-beteende eller config-authority paths.
- Alla destruktiva åtgärder kräver separat kontrakt (P1/P2).
