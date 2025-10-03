# Changelog

Formatet följer en förenklad variant av Keep a Changelog. Versionsnumrering enligt SemVer (pre‑1.0: brytande ändringar => minor‑bump).

## [0.2.0] - 2025-10-03

- Added
  - SSOT Runtime Config API: `GET /config/runtime`, `POST /config/runtime/validate`, `POST /config/runtime/propose` (optimistisk låsning via `expected_version`).
  - Bearer‑auth för `POST /config/runtime/propose` via env `BEARER_TOKEN` (skickas som `Authorization: Bearer <token>`).
  - UI‑statuspanel: visar `config_version/hash` från `/health` och uppdateras efter lyckad `propose`.
  - UI‑stöd för `propose`: sparar bearer‑token i `localStorage.ui_bearer` och sänder korrekt header.
  - SymbolMapper i REST/WS/Client: central symbolnormalisering mellan mänskliga (`BTCUSD`) och Bitfinex/TEST (`tBTCUSD`/`tTESTBTC:TESTUSD`) styrt av `SYMBOL_MODE=realistic|synthetic`.
  - Seed av runtime: `config/runtime.json` seeds från `config/runtime.seed.json` om fil saknas (första start). `config/runtime.json` är git‑ignorerad.
  - Audit‑logg med rotation: ändringar skrivs till `logs/config_audit.jsonl` och roteras när filen är ~5 MB. Audit innehåller `actor`, `expected_version/new_version`, `hash_before/after`, och ändrade `paths`.

- Changed
  - SSOT ersätter tidigare ad‑hoc/override‑flöden i UI. Kommentar och logik för overrides är borttagen/inaktiverad när SSOT används.
  - Säkerhetsnivå höjd för runtime‑ändringar (Bearer‑auth gate och strikt whitelist av tillåtna patch‑fält: `thresholds`, `gates`, `risk.risk_map`, `ev.R_default`).

- Removed
  - Legacy config‑endpoints (`/config/validate`, `/config/diff`, `/config/audit`) borttagna ur API:t. Dokumentation som fortfarande nämner dem kommer att uppdateras i nästa release.

- Migration
  - Klienter/skript ska byta till:
    - Läsning: `GET /config/runtime` → `{ cfg, version, hash }`.
    - Validering: `POST /config/runtime/validate` med hela config‑objektet.
    - Ändringsförslag: `POST /config/runtime/propose` med body `{ patch, actor, expected_version }` och header `Authorization: Bearer <token>`.
  - UI: fyll i bearer‑token i fältet och klicka "Föreslå ändring"; statuspanelen uppdateras automatiskt.

- QA/Tests
  - E2E‑test för config‑API som verifierar 401 utan korrekt Bearer och success med korrekt token.
  - Enhetstester för `SymbolMapper` och integrering i REST/WS.

### Versionsbump (förslag)

- Föreslagen bump: 0.1.0 → 0.2.0 (brytande ändringar p.g.a. borttagna legacy‑endpoints och nytt SSOT‑flöde).

### Nästa release‑steg

1. Uppdatera versionsnummer i `pyproject.toml` → `version = "0.2.0"`.
2. Uppdatera dokumentation som fortfarande refererar till `/config/validate`, `/config/diff`, `/config/audit` och `/dev/overrides` till nya SSOT‑endpoints.
3. Lägg till `BEARER_TOKEN=` i `.env.example` (tomt värde som exempel) och beskriv i README hur den används.
4. Kör lokalt CI:
   - Windows PowerShell:
     ```powershell
     .\scripts\ci.ps1
     ```
5. Rök/acceptanstest:
   - Starta appen och verifiera:
     - `GET /health` visar `config_version/hash`.
     - `GET /config/runtime` fungerar.
     - `POST /config/runtime/propose` med korrekt Bearer höjer versionen och skriver audit.
     - UI visar version/hash och lyckas med `Föreslå ändring`.
6. Skapa commit och tagg:
   ```powershell
   git add CHANGELOG.md pyproject.toml README.md docs
   git commit -m "chore(release): v0.2.0 – SSOT runtime, Bearer‑auth, SymbolMapper, seed, audit‑rotation, UI‑status/propose, drop legacy endpoints"
   git tag -a v0.2.0 -m "Genesis-Core v0.2.0"
   git push && git push --tags
   ```
7. Publicera release‑notiser med kort sammanfattning (detta innehåll) och länka till relevanta sektioner i README.
