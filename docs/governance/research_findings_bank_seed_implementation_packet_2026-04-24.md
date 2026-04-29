# Research findings bank seed implementation packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / non-runtime seed implementation / repo-native findings bank`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — non-runtime evidence tracking only; no `src/**`, `tests/**`, `config/**`, `registry/**`, or runtime/default/promotion surfaces changed.
- **Required Path:** `Small non-trivial RESEARCH docs/evidence path (not Quick); reduced non-runtime validation only.`
- **Lane:** `Research-evidence` — the cheapest admissible next step is to materialize a small, traceable findings bank for the current RI-router case before any further runtime candidate is authored.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** seed a repo-native findings bank with a minimal bundle schema, a small set of current RI-router findings, matching ledger `ArtifactRecord` registrations, and one derived findings index.
- **Candidate:** `research findings bank seed slice`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/research_findings_bank_repo_native_packet_2026-04-24.md`
  - `docs/analysis/research_findings_bank_repo_native_structure_2026-04-24.md`
  - `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- **Candidate / comparison surface:**
  - new finding bundles under `artifacts/bundles/findings/ri_policy_router/**`
  - matching ledger records under `artifacts/research_ledger/artifacts/**`
  - one derived view under `artifacts/research_ledger/indexes/findings_index.json`
- **Vad ska förbättras:**
  - preserve both positive and negative findings so later slices can reuse verified conclusions and avoid duplicate work
  - keep the conclusions searchable by verdict, seam class, timestamps, and evidence refs
- **Vad får inte brytas / drifta:**
  - no new runtime authority
  - no new ledger entity type
  - no mutation of candidate registry semantics
  - no external database dependency
- **Reproducerbar evidens som måste finnas:**
  - every seeded finding must point at repo-visible evidence docs and/or artifact paths
  - the derived findings index must be deterministic and bundle-derived

### Scope

- **Scope IN:**
  - `docs/governance/research_findings_bank_seed_implementation_packet_2026-04-24.md`
  - `artifacts/bundles/findings/schema/research_findings_bundle_v1.schema.json`
  - `artifacts/bundles/findings/ri_policy_router/*.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0002.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0003.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0004.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0005.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0006.json`
  - `artifacts/research_ledger/indexes/findings_index.json`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `registry/**`
  - `config/**`
  - any runtime/backtest reruns
  - any new ledger entity type, storage semantics, or query API
  - any promotion/champion/readiness/family-rule surface
- **Expected changed files:**
  - one packet doc
  - one finding bundle schema file
  - five seeded finding bundle JSON files
  - five seeded ledger artifact records
  - one derived findings index
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `14`

### Gates required

- editor validation for changed markdown/json files (`Problems` clean)
- deterministic JSON parse check over the seeded finding bundles, seeded ledger artifacts, and `findings_index.json`

### Required seeded finding-outcome coverage

The seed set must include at least:

1. one **positive** finding
2. one **negative** finding
3. one **direction-lock** finding

Reason:

- preserving only failures would lose reusable wins,
- preserving only wins would repeat already-vetoed work,
- preserving blocked/direction-lock findings prevents repeated seam conflation and duplicate candidate framing.

### Required finding bundle fields

Every seed bundle must carry at minimum:

- `finding_id`
- `created_at`
- `subject`
- `domain`
- `candidate_refs`
- `finding_outcome`
- `summary`
- `mechanism`
- `key_timestamps`
- `evidence_refs`
- `next_admissible_step`
- `runtime_authority`

`finding_outcome` is research-only evidence direction (for example `positive`,
`negative`, `direction_lock`) and is not a governance verdict. It carries no
runtime, promotion, readiness, or family authority.

### Stop Conditions

- any bundle implies runtime authority or executable config meaning
- the index becomes the only source of truth instead of a derived projection
- seeded findings omit verdict diversity and only preserve one side of the evidence
- seeded findings paraphrase conclusions without pointing to actual repo-visible evidence refs

## Bottom line

This packet authorizes a small, non-runtime seed implementation of the findings bank for the current RI-router case.
It exists to preserve both good and bad findings, plus blocked seam-direction conclusions, so later slices do not repeat already resolved work.
