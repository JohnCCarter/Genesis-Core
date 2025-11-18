# Cursor-baslinje

**Senast uppdaterad:** 2025-10-31

Detta dokument beskriver den minsta Cursor-konfigurationen som krävs för att arbetet i stabiliseringsfasen ska fungera utan överraskningar. Utgå från denna lista inför varje handoff.

## 1. Grundläggande inställningar (`%APPDATA%/Cursor/User/settings.json`)

- `github.copilot.enable`: `"*": true`, `"scminput": false` – säkerställer att Cursor- och Copilot-agenter fungerar i kod men inte i commit-meddelanden.
- `editor.formatOnSave`: `true` – nyttjar definierade formatterare (Black/Prettier).
- `editor.unicodeHighlight.invisibleCharacters`: `true` och `editor.unicodeHighlight.ambiguousCharacters`: `true` – fångar osynliga tecken i Python/YAML.
- `update.releaseTrack`: `stable` – undviker prerelease-regressioner under stabiliseringsfasen.
- `files.exclude` och `search.exclude`: inkludera `**/.venv`, `**/__pycache__`, `**/.mypy_cache`, `**/.log` för renare sökningar.
- Övriga språkformatterare definierade i befintlig fil (Black/Prettier m.fl.) ska lämnas oförändrade.

## 2. Obligatoriska extensioner (`code --list-extensions`)

- `ms-python.python`, `ms-python.debugpy`, `ms-python.black-formatter`
- `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`
- `github.copilot`, `github.copilot-chat`, `ms-vscode.vscode-copilot-data-analysis`, `ms-vscode.vscode-copilot-vision`, `ms-vscode.vscode-websearchforcopilot`
- `ms-vscode.powershell` (Windows-shell workflow)
- `bar.python-import-helper`, `kevinrose.vsc-python-indent`, `njpwerner.autodocstring`
- `mechatroner.rainbow-csv`, `ms-toolsai.datawrangler`
- `github.codespaces`, `github.vscode-pull-request-github`, `github.vscode-github-actions`
- `openai.chatgpt` (explicit önskemål att behålla)

## 3. Verifiering

1. Kör `code --list-extensions` och stäm av mot listan ovan.
2. Öppna en Python-fil och kontrollera att format-on-save triggar Black (via statusfältet).
3. Klistra in ett osynligt tecken (t.ex. zero-width space) och bekräfta att Cursor varnar.
4. Kör `Cursor: Reload Window` efter ändringar för att säkerställa att inställningarna laddas.

## 4. Handoff-påminnelser

- Dokumentera eventuella avvikelser i `docs/daily_summaries/daily_summary_YYYY-MM-DD.md`.
- Vid nya verktyg: uppdatera både detta dokument och `cursor-active-rules.mdc`.
- För större miljöändringar: koordinera med nästa agent innan Optuna-körningar startas.
