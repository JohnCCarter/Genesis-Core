# Research findings preflight lookup implementation packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical implementation snapshot / consumed by non-runtime lookup helper / no active packet authority`

> Current status note:
>
> - HISTORICAL 2026-05-05: this file records the bounded implementation authorization for the non-runtime findings preflight lookup helper on `feature/ri-role-map-implementation-2026-03-24`, not an active packet authority on `feature/next-slice-2026-05-05`.
> - Its implementation role is reflected in `scripts/preflight/findings_preflight_lookup.py` and `tests/utils/test_findings_preflight_lookup.py`.
> - Preserve this file as historical lookup-governance provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `LOW` — non-runtime research-support helper only; no strategy runtime, config authority, registry semantics, or ledger storage behavior is changed.
- **Required Path:** `Small non-trivial RESEARCH tooling path; reduced non-runtime validation only.`
- **Lane:** `Research-evidence` — the cheapest admissible next step is to add a preflight lookup against the existing findings bank so new slices can reuse known conclusions before authoring more packets or candidates.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** implement a small lookup/preflight helper that queries the existing findings bank by filters such as domain, symbol, timeframe, seam class, outcome, candidate refs, and free text, and can optionally fail when blocking matches exist.
- **Candidate:** `research findings preflight lookup`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: small Python script/test slice with targeted lint and pytest validation.
- **No additional repo-local skill required**
  - reason: `src/**`, runtime, backtest, and config-authority surfaces remain OUT.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/research_findings/research_findings_bank_repo_native_packet_2026-04-24.md`
  - `docs/decisions/research_findings/research_findings_bank_seed_implementation_packet_2026-04-24.md`
  - `artifacts/research_ledger/indexes/findings_index.json`
- **Candidate / comparison surface:**
  - one preflight helper under `scripts/preflight/`
  - one focused test file under `tests/utils/`
- **Vad ska förbättras:**
  - stop duplicate work before a new candidate/packet is framed
  - surface positive findings worth reusing and negative/direction-lock findings worth avoiding
- **Vad får inte brytas / drifta:**
  - no new runtime authority
  - no mutation of findings-bank source-of-truth files
  - no new ledger entity types or storage semantics
  - no promotion/readiness/governance-gate semantics
- **Reproducerbar evidens som måste finnas:**
  - deterministic lookup over the current findings index and linked bundles
  - focused tests proving filter behavior and blocking-match exit behavior

### Scope

- **Scope IN:**
  - `docs/decisions/research_findings/research_findings_preflight_lookup_implementation_packet_2026-04-24.md`
  - `scripts/preflight/findings_preflight_lookup.py`
  - `tests/utils/test_findings_preflight_lookup.py`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `registry/**`
  - mutation of `artifacts/bundles/findings/**`
  - mutation of `artifacts/research_ledger/**`
  - any new schema or index format changes
  - any runtime/backtest execution or candidate semantics change
  - any promotion/champion/readiness/family-rule surface
- **Expected changed files:**
  - one packet doc
  - one helper script
  - one focused test file
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `4`

### Proposed helper behavior

The helper may:

- read `artifacts/research_ledger/indexes/findings_index.json`
- resolve linked bundle files for richer details
- filter by exact fields and substring search
- print human-readable grouped output and optional JSON output
- return non-zero when `--fail-on-blocking-match` is set and at least one filtered finding has structured `finding_outcome` exactly `negative` or `direction_lock`

The helper must not:

- rewrite findings-bank artifacts
- infer governance authority from findings
- treat `positive` findings as blockers
- create or mutate any runtime/config surface

Read-only lookup access to existing files under `artifacts/bundles/findings/**` and
`artifacts/research_ledger/**` is allowed for this helper. Those paths remain OUT
for modification.

`--fail-on-blocking-match` is a research preflight convenience only. It must stay
opt-in, exact-field based, and non-authoritative. It does not create runtime,
promotion, readiness, or family-rule authority.

A non-zero exit from `--fail-on-blocking-match` means only that the current
filtered result set contains at least one structured `finding_outcome` of
`negative` or `direction_lock`. It is advisory only and does not create runtime,
governance, or promotion authority.

### Gates required

- editor validation for changed `.md` and `.py` files (`Problems` clean)
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/preflight/findings_preflight_lookup.py tests/utils/test_findings_preflight_lookup.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_findings_preflight_lookup.py`
- one script smoke run against the current repo findings bank
- runtime-only replay / feature-cache / pipeline-invariant gates are `N/A` for this slice because `src/**` and runtime pipeline surfaces remain OUT

### Stop Conditions

- any need to mutate findings-bank artifacts during lookup
- any need to add new runtime or ledger storage semantics
- any need to reinterpret findings as governance verdicts or promotion authority
- helper scope drifts into packet/candidate authoring automation in the same slice

## Bottom line

This packet authorizes one small non-runtime helper that makes the seeded findings bank usable as a duplicate-work guard before the next slice is framed.
