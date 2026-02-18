# Scripts i Genesis-Core

Detta dokument beskriver hur script i `scripts/` organiseras, auditeras och avvecklas säkert.

## Kategorier

- **stable**
  - Script som används i ordinarie arbetsflöden (backtest, validering, preflight, produktion/paper-support).
- **ops**
  - Operativa script för drift, felsökning, health checks och miljöstöd.
- **experimental**
  - Script för tillfälliga experiment/hypoteser. Ska inte vara implicit del av produktionsflöde.
- **deprecated**
  - Script som har flyttats till archive men fortfarande har wrapper på gamla pathen.
- **archive**
  - Historiska script under `scripts/archive/**`. Behandlas som dead zone för intern referensräkning.

## Policy för säker städning

1. **Inga hårda raderingar direkt**.
2. Flytta script med `git mv` till `scripts/archive/YYYY-MM/...`.
3. Lämna wrapper på gamla pathen som:
   - skriver tydlig `DEPRECATED`-varning,
   - vidarebefordrar alla argument,

- returnerar samma exit code,
- loggar användning (en rad per körning) i `scripts/deprecated-usage.log`.

4. **Radera tidigast efter 14 dagar** från deprecate-flytt.
5. Under 14-dagarsfönstret ska gamla paths fortsätta fungera via wrappers.

## Kör scripts-audit

Exempel:

`python scripts/audit_scripts.py --root . --scripts-dir scripts --out reports/scripts_audit.csv --out-md reports/scripts_audit.md`

Auditrapporten innehåller bland annat:

- path
- filtyp/ext
- antal rader
- filstorlek
- senast ändrad (git om möjligt)
- interna referenser i repot
- riskflaggor och kandidatscore

Noteringar:

- `scripts/archive/**` ignoreras vid intern referensräkning (dead zone).
- Stora/genererade mappar exkluderas från referenssökning (`data/`, `results/`, `.venv/`, `node_modules/`, `dist/`, `build/`, `__pycache__/`, `.git/`).

## Deprecate-flytta ett script

### Dry-run (rekommenderad först)

`python scripts/deprecate_move.py --source scripts/<script>.py --archive-subdir <kategori> --dry-run`

### Utför flytt + wrapper

`python scripts/deprecate_move.py --source scripts/<script>.py --archive-subdir <kategori>`

Valfria flaggor:

- `--archive-month YYYY-MM` för att skriva till specifik arkivmånad.

Wrapper-beteende per filtyp:

- `.py`: varning till stderr + körning via `runpy.run_path(..., run_name="__main__")`
- `.ps1`: `Write-Warning` + `& <newpath> @args` + `exit $LASTEXITCODE`
- `.sh`: varning till stderr + `exec bash <newpath> "$@"`

## Rekommenderat arbetssätt

1. Kör audit.
2. Välj kandidat med tydlig evidens (refs/risk/ålder/storlek).
3. Kör `deprecate_move.py` i dry-run.
4. Kör skarp move + wrapper.
5. Verifiera att befintliga anrop fortfarande fungerar.
6. Vänta minst 14 dagar innan eventuell slutlig borttagning.

## Checklista för radering (efter deprecation window)

1. Minst 14 dagar har passerat sedan flytt till `scripts/archive/YYYY-MM/...`.
2. `scripts/deprecated-usage.log` visar **0 usage** för scriptets wrapper under hela 14-dagarsperioden.
3. Externa triggers är verifierade innan radering:

- Windows Task Scheduler
- cron
- CI schedules

4. Radera i två steg:

- först wrapper på gamla pathen,
- därefter (valfritt) archive-kopian efter ytterligare grace-period.
