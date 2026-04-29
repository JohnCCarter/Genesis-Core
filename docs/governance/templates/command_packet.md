# Command Packet (v1.1)

Kopiera mallen nedan för varje ny uppgift.

## COMMAND PACKET

- **Mode:** `(STRICT/RESEARCH/SANDBOX)` — source: `docs/governance_mode.md`
- **Risk:** `(LOW/MED/HIGH)` — why:
- **Required Path:** `(Quick/Lite/Full)`
- **Lane:** `(Concept/Research-evidence/Runtime-integration)` — why this is the cheapest admissible lane now:
- **Objective:**
- **Candidate:** (om relevant)
- **Base SHA:**

### Lane framing

Fyll endast i den lane-del som faktiskt gäller.
Lane-val är workflow guidance only.
Det ändrar inte governance mode-resolution, authority precedence, freeze rules eller required gates för runtime-/kodändringar.
Det hjälper bara till att välja proportionerlig validering för den aktuella docs-/concept-/evidence-slicen.

#### Concept lane

- **Hypotes / idé:**
- **Varför det kan vara bättre:**
- **Vad skulle falsifiera idén:**
- **Billigaste tillåtna ytor:** (`docs/analysis/**`, `results/research/**`, replay/trace, `tmp/**`, researchscripts)
- **Nästa bounded evidence-steg:**

#### Research-evidence lane

- **Baseline / frozen references:**
- **Candidate / comparison surface:**
- **Vad ska förbättras:**
- **Vad får inte brytas / drifta:**
- **Reproducerbar evidens som måste finnas:**

#### Runtime-integration lane

- **Durable surface som föreslås:**
- **Varför billigare icke-runtime-form inte längre räcker:**
- **Default-path stance:** `(unchanged / explicit exception required)`
- **Required packet / review:**

### Scope

- **Scope IN:**
- **Scope OUT:**
- **Expected changed files:**
- **Max files touched:**

### Gates required

Välj minsta lane- och path-appropriate gates enligt `.github/copilot-instructions.md`.
Koncept-/docs-only-slices ska inte automatiskt bära runtime-klassade gates om scope inte kräver det.

- `pre-commit run --all-files`
- `pytest -q`
- Selectors (om relevant):
  - determinism replay
  - feature cache invariance
  - pipeline hash guard
  - freeze guard checks

### Stop Conditions

- Scope drift
- Behavior change utan explicit undantag
- Hash/determinism regression
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
