# Research findings packet starter implementation packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / pre-code / non-runtime advisory starter helper`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `LOW` — non-runtime research-support helper only; no runtime strategy, config authority, registry semantics, or findings-bank storage behavior changes.
- **Required Path:** `Small non-trivial RESEARCH tooling path; reduced non-runtime validation only.`
- **Lane:** `Research-evidence` — the cheapest admissible next step is to layer an advisory packet starter on top of the existing findings lookup so later slices can begin from prior evidence instead of manually reassembling the same constraints.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** implement a small read-only helper that reuses the findings lookup surface and emits advisory markdown/JSON starter content for new candidate or analysis packets without writing files or creating new authority.
- **Candidate:** `research findings packet starter`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: small Python script/test slice with targeted lint and pytest validation.
- **No additional repo-local skill required**
  - reason: `src/**`, runtime, backtest, and config-authority surfaces remain OUT.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/research_findings_preflight_lookup_implementation_packet_2026-04-24.md`
  - `scripts/preflight/findings_preflight_lookup.py`
  - `artifacts/research_ledger/indexes/findings_index.json`
- **Candidate / comparison surface:**
  - one advisory starter helper under `scripts/preflight/`
  - one focused test file under `tests/utils/`
- **Vad ska förbättras:**
  - reduce manual packet framing effort after lookup
  - surface reusable positive anchors, blockers, `do_not_repeat`, and `next_admissible_step` hints in one ready-to-paste starter output
- **Vad får inte brytas / drifta:**
  - no file creation or mutation by the helper itself
  - no new findings-bank authority or semantics
  - no runtime/governance/promotion authority claims
  - no automatic packet authoring beyond advisory stdout/json output
  - `scripts/preflight/findings_preflight_lookup.py` remains a read-only dependency and out of implementation scope for this slice
- **Reproducerbar evidens som måste finnas:**
  - deterministic starter content from filtered findings-bank results
  - focused tests proving ordered deduplication and advisory-only output structure

### Scope

- **Scope IN:**
  - `docs/decisions/research_findings_packet_starter_implementation_packet_2026-04-24.md`
  - `scripts/preflight/findings_packet_starter.py`
  - `tests/utils/test_findings_packet_starter.py`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `registry/**`
  - mutation of `artifacts/bundles/findings/**`
  - mutation of `artifacts/research_ledger/**`
  - automatic writes under `docs/**`
  - any runtime/backtest execution or candidate semantics change
  - any governance verdict, readiness, promotion, or family-rule surface
- **Expected changed files:**
  - one packet doc
  - one advisory starter script
  - one focused test file
- **Max files touched:** `3`

### Proposed helper behavior

The helper may:

- reuse the existing findings lookup surface to filter findings by domain, symbol, timeframe, seam class, outcome, refs, timestamps, and free text
- emit advisory markdown starter content to stdout
- emit machine-readable JSON starter content to stdout
- group matched findings into positive anchors, blockers/direction locks, `do_not_repeat`, `next_admissible_step`, and reference lists
- deduplicate repeated hints while preserving first-seen order

The helper must not:

- write or modify packet files
- mutate findings-bank artifacts
- infer governance authority from matched findings
- convert advisory hints into automatic decisions or runtime semantics

The starter output is advisory only. It may summarize and reorganize already stored
finding content, but it does not create runtime, governance, readiness, or promotion
authority, and it must not be described as an automatic packet author.

All grouped sections must stay citation-backed summaries of matched findings for
manual copy/paste only. Optional JSON output is a convenience serialization of the
same advisory content and is not a stable authority or promotion API.

### Gates required

- editor validation for changed `.md` and `.py` files (`Problems` clean; supplemental only)
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/preflight/findings_packet_starter.py tests/utils/test_findings_packet_starter.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_findings_packet_starter.py`
- one script smoke run against the current repo findings bank
- runtime-only replay / feature-cache / pipeline-invariant gates are `N/A` for this slice because `src/**` and runtime pipeline surfaces remain OUT

### Stop Conditions

- any need for the helper to write files directly under `docs/**`
- any need to mutate findings-bank artifacts during starter generation
- any need to reinterpret findings as governance verdicts or runtime authority
- helper scope drifts into packet creation, packet editing, or other write automation in the same slice

## Bottom line

This packet authorizes one small non-runtime helper that turns filtered findings-bank results into an advisory packet-starting surface without creating new authority or file-writing automation.
