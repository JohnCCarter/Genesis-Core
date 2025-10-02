### README för AI‑agenter (lokal utveckling)

Denna fil beskriver hur AI‑agenter ska arbeta lokalt med projektet.

#### Regler
- Följ Separation of concerns: `core/strategy/*` är rena, deterministiska funktioner.
- Inga hemligheter i loggar; använd `core.utils.logging_redaction` vid behov.
- Pausa vid osäkerhet, verifiera med tester innan du fortsätter.
- Skriv alltid enhetstester när du lägger till logik. Håll latens per modul < 20 ms.
- Använd `metrics` endast i orkestreringslager (`core/strategy/evaluate.py`), inte i pure‑moduler.

#### Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

#### CI lokalt
```powershell
pwsh -File scripts/ci.ps1
```

#### Kör FastAPI lokalt
```powershell
uvicorn core.server:app --reload --app-dir src
```

#### Strategy‑pipeline lokalt
Se exempel i `README.md` (GitHub‑läsare) eller kör tester:
```powershell
python -m pytest -q
```

#### Dev overrides (lokalt)
- Behåll prod‑lika defaults i `config/strategy/defaults.json`.
- Sätt lokala testtrösklar via UI‑rutan eller en privat fil `dev.overrides.local.json` (git‑ignorerad).
- Exempel: `dev.overrides.example.json` (kopiera till `dev.overrides.local.json` och justera vid behov).
- Vid API‑körning: skicka overrides i body till `POST /strategy/evaluate` under nyckeln `configs`.

#### Filstruktur (kärna)
- `src/core/strategy/features.py` – tidsrättade features, percentilklipp
- `src/core/strategy/prob_model.py` – `predict_proba` + `predict_proba_for`
- `src/core/strategy/confidence.py` – monotoni + clamp [0,1]
- `src/core/strategy/regime.py` – HTF + hysteresis/state
- `src/core/strategy/decision.py` – gate‑ordning, fail‑safe, sizing
- `src/core/strategy/evaluate.py` – orkestrering + observability

#### Testfiler
- `tests/test_features.py`
- `tests/test_prob_model_integration.py`
- `tests/test_confidence.py`
- `tests/test_regime.py`
- `tests/test_decision.py`
- `tests/test_e2e_pipeline.py`

#### Vanliga fel och åtgärder
- Time alignment: använd endast stängda barer (se testerna för `now_index`).
- Dubbeljustering: lägg spread/volym‑påverkan i confidence/policy, inte i probability/regime.
- NaN/Inf: clampa i features/confidence.


