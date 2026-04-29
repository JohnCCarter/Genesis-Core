# Concept / evidence / runtime lane model

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `docs-only / workflow guidance / no-runtime-authority`

This document is practical workflow guidance for Genesis-Core.

It does **not** change:

- governance mode resolution (`docs/governance_mode.md` remains SSOT)
- authority precedence (`.github/copilot-instructions.md` remains the practical SSOT)
- strict-only surfaces
- freeze rules
- runtime/default/promotion authority
- the requirement for separate packets, Opus review, and verification before non-trivial integration work

This is a workflow model, not a new mode system.

## Purpose

The repository needs a cheaper place to think and falsify ideas before they become expensive runtime structure.

The purpose of this model is therefore to separate three different kinds of work that otherwise tend to drift together:

1. thinking about candidate ideas
2. proving whether a candidate actually holds up
3. integrating something into runtime-relevant structure

The operating principle is simple:

- think cheaply
- prove reproducibly
- integrate cautiously

## What this model is not

This document does **not**:

- authorize runtime changes
- authorize family creation by itself
- authorize promotion, readiness, cutover, or deployment claims
- replace command packets or commit contracts
- reduce any existing verification or review requirements
- require a separate repository

Historical packet/report docs under `docs/governance/**` remain dated snapshots and should not be mass-rewritten to fit this language unless they become directly contradictory in active use.

## Relationship to governance mode

Modes answer **how strict** the work must be.

- `STRICT`
- `RESEARCH`
- `SANDBOX`

Lanes answer **what kind of work** is being done.

- concept lane
- research-evidence lane
- runtime-integration lane

The lane model does not override mode resolution. A lane still operates under the mode determined by `docs/governance_mode.md` and the higher-order governance files.

## Lane 1 — Concept lane

### Purpose

The concept lane exists to test ideas before they are treated as runtime form.

Typical work in this lane includes:

- role-map ideas
- policy hypotheses
- alternative structural interpretations
- replay-/trace-based analysis
- research scripts
- `docs/analysis/**`
- comparisons against frozen artifacts

### Expected outputs

The output should usually be small and explicit:

- a candidate idea
- why it might be better
- what would falsify it
- what would need to be measured next

### Allowed stance

Concept work may be incomplete, provisional, and exploratory.

It may use approximations, reduced taxonomies, or temporary analysis structure when clearly marked as such.

### Must not

Concept work must not, by implication or convenience:

- create runtime authority
- create promotion authority
- create readiness authority
- present itself as runtime-ready
- create a new strategy family just because research needs a new container

## Lane 2 — Research-evidence lane

### Purpose

The research-evidence lane exists to answer whether a concept actually holds up under reproducible scrutiny.

Questions for this lane include:

- does the idea work?
- is it reproducible?
- what improves?
- what degrades?
- what remains unchanged?

### Expected outputs

Typical outputs include:

- deterministic comparisons
- bounded replay results
- documented baseline/candidate framing
- evidence summaries
- PASS / FAIL / inconclusive conclusions

### Allowed stance

This lane is more disciplined than concept work, but it is still not runtime integration.

It may add bounded, explicit, additive evidence surfaces when separately governed and when default behavior remains unchanged.

### Must not

Research-evidence work must not:

- claim runtime authority
- claim promotion authority
- claim readiness or cutover status
- smuggle in default changes
- turn research results directly into family/runtime semantics without a separate integration slice

## Lane 3 — Runtime-integration lane

### Purpose

The runtime-integration lane is where something may finally become merge-relevant runtime structure.

Only here may work propose or implement things such as:

- family semantics
- runtime paths
- authority-adjacent public structure
- merge-relevant durable control surfaces

### Why this lane is intentionally expensive

This lane is expensive by design because this is where:

- determinism obligations matter most
- default behavior discipline matters most
- rollback cost rises
- future research starts depending on the structure being stable

### Required posture

Runtime-integration work must continue to use the existing governed path:

- explicit command packet / commit contract
- Opus pre-code review when required
- minimal scoped diff
- appropriate gates
- post-diff audit when required

This document does not reduce those obligations.

## Family rule

Strategy families are expensive runtime/public shapes.

They should not be used as the repository's default container for early research.

Before proposing a new family, prefer testing whether the idea can live as one of the following first:

- role-map candidate
- policy candidate
- replay profile
- selector version
- bounded comparison surface

Operational rule:

- no new strategy family should be introduced until simpler non-runtime forms are shown to be insufficient for the work being attempted

## Promotion rules between lanes

### Concept -> research-evidence

Promote a concept only when all are true:

- the hypothesis is explicit
- a baseline is identified
- falsification criteria are stated
- the next bounded evidence step is clear

### Research-evidence -> runtime-integration

Promote evidence work only when all are true:

- the result is reproducible
- the improvement and degradation are both understood
- default behavior can remain unchanged or a separate explicit exception is requested
- the work can explain why a cheaper non-runtime form is no longer sufficient
- a fresh integration packet can be scoped tightly

Evidence alone is not integration authority.

## Surface cost guidance

### Cheaper surfaces

Examples of cheaper research surfaces include:

- `tmp/**`
- `docs/analysis/**`
- `docs/bugs/**`
- `results/research/**`
- read-only replay and trace analysis

### More governed but still pre-runtime surfaces

Examples include:

- reusable research comparison helpers
- deterministic replay harnesses
- additive evidence packaging
- bounded observability helpers that remain explicitly non-authoritative

### Expensive surfaces

Expensive surfaces remain the existing runtime/default/authority-sensitive areas already protected by the repository governance files, including strict-only and freeze-sensitive zones.

This document does not redefine them.

## Short decision checklist

Before opening a new slice, ask:

1. Which lane is this really?
2. What would falsify the claim?
3. Are we accidentally turning a hypothesis into runtime form?
4. Why is a cheaper non-runtime shape not enough?
5. If runtime structure is proposed, why must it be durable now?

## Canonical usage rule

This document is the canonical practical definition of the three-lane workflow model.

Other repository documents may:

- summarize it briefly
- reference it
- explain how their own workflow maps to it

Other repository documents should not duplicate the full definition unless a higher-order governance change explicitly requires it.

## Related references

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/governance_mode.md`
- `docs/governance/README.md`
- `CLAUDE.md`
