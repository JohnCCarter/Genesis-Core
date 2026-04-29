# Document taxonomy migration slice 1 packet — 2026-04-29

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `smallest admissible non-trivial RESEARCH docs migration path`
- **Lane:** `Concept` — cheapest admissible lane because this slice only relocates historical documentation into already-defined taxonomy zones without changing runtime, config, or authority semantics
- **Skill Usage:** `repo_clean_refactor` — bounded documentation migration under no-behavior-change and strict-scope constraints
- **Objective:** migrate one small active-lane RI policy-router document batch into the right folders so the new taxonomy is proven on real historical docs without widening into bulk migration
- **Candidate:** `document taxonomy migration slice 1`
- **Base SHA:** `d5778913`

### Concept lane

- **Hypotes / idé:** en liten verklig flytt av den senaste RI policy-router-trion ger bättre navigering och authority-separation än att lämna allt historiskt under `docs/governance/`.
- **Varför det kan vara bättre:** det visar den nya taxonomin i praktiken, minskar signalbrus i governance-mappen och gör aktiva evidens- och packet-ankare lättare att läsa rätt.
- **Vad skulle falsifiera idén:** om flytten kräver bred historisk korslänksstädning, skapar oklarhet om authority, eller visar att dokumentklasserna inte går att separera utan större ommodellering.
- **Billigaste tillåtna ytor:** `docs/decisions/**`, `docs/analysis/**`, `GENESIS_WORKING_CONTRACT.md`
- **Nästa bounded evidence-steg:** om denna lilla batch landar rent kan nästa migreringsslice ta en annan tydlig dokumentklass i stället för att massflytta hela `docs/governance/`.

### Scope

- **Scope IN:**
  - move `docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md` into the decisions zone
  - move `docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md` into the analysis zone
  - move `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md` into the analysis zone
  - update exact path references in the moved files and `GENESIS_WORKING_CONTRACT.md`
  - add this migration decision record
- **Scope OUT:**
  - no runtime/code/config changes
  - no movement of the 2026-04-28 predecessor analysis notes yet
  - no mass migration of governance packets or closeouts
  - no `.gitignore`, CI, or enforcement changes
  - no results or artifacts migration
  - no broad historical crosslink rewrite beyond exact moved-path references
- **Expected changed files:** `5`
- **Max files touched:** `6`

### Gates required

- `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md docs/analysis/regime_intelligence/policy_router/ri_policy_router_defensive_probe_exact_carrier_evidence_2026-04-29.md docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md docs/decisions/document_taxonomy_migration_slice1_packet_2026-04-29.md`
- `git diff --stat`
- `git diff`
- exact-path search for the old file names
- focused manual link/path review of touched docs

### Stop Conditions

- scope drift beyond the moved trio, the working contract, and this packet
- wording that implies governance authority changed just because the files moved
- need for `.gitignore` or CI repair to complete the slice
- any requirement to reinterpret runtime behavior or reopen tuning as part of the migration

### Non-goals

- no content-semantic rewrite of the migrated notes
- no claim that all older governance docs are now fully reclassified
- no change to evidence verdicts or policy conclusions
- no migration of predecessor `2026-04-28` notes in the same slice

### Output required

- one small decision record for the migration slice
- moved docs with exact path updates only where needed
- updated working anchor paths
- scope containment proof via `git diff --stat`
