# Evidence claim header template

Status: `complementary template / governance helper / no authority`

Use this template for **claim-bearing evidence notes** — that is, notes or summaries that make reproducibility, comparison, provenance, or boundary claims likely to influence a later packet, decision, or review.

This template is **not** meant to turn every scratch note into a heavyweight ritual.

## Use this template when

- the note claims a result is reproducible
- the note compares baseline versus candidate behavior
- the note cites an artifact hash or frozen bundle
- the note may later be referenced in a packet, signoff, promotion argument, or runtime-adjacent discussion

## A lighter note is still okay when

- the work is exploratory and clearly marked as such
- no new artifact or reproducibility claim is being made
- the note is just a question, hunch, or local scratch read

## Minimum fields for a claim-bearing note

At minimum, capture:

- authority level
- claim status (`observed`, `inferred`, `unverified`)
- runtime base SHA
- evidence commit SHA, or an explicit note that the current slice did not rerun the evidence
- config path and hash when relevant
- symbol/timeframe/window/warmup when relevant
- data-source policy
- symbol mode
- relevant env flags
- cache policy
- working-tree clean/dirty status
- artifact path(s) and hash(es) when generated or cited
- a short `does not authorize` boundary

## Copyable header

```md
## Claim header

- **Date:**
- **Branch:**
- **Mode:** `STRICT | RESEARCH | SANDBOX` — source:
- **Lane:** `Concept | Research-evidence | Runtime-integration` — why:
- **Status:** `observational / evidence summary / comparison / planning-only`
- **Authority level:** `observational only / bounded research-evidence / historical reference / other`
- **Claim status:** `observed / inferred / unverified`
- **Objective:**
- **Baseline reference(s):**
- **Candidate / comparison surface:**
- **Runtime base SHA:**
- **Evidence commit SHA:**
- **Working-tree status:** `clean / dirty / not checked in this slice`
- **Config path:**
- **Config hash:**
- **Symbol / timeframe:**
- **Window:**
- **Warmup:**
- **Data-source policy:**
- **Symbol mode:**
- **Env flags:**
- **Cache policy:**
- **Artifact path(s):**
- **Artifact hash(es):**
- **What changed:**
- **What did not change:**
- **Does not authorize:**
```

## Guidance

### 1. Do not guess missing provenance

If the current slice did **not** rerun the evidence, say so explicitly instead of backfilling guessed values.

Good:

- `Evidence commit SHA: not rerun in this slice; citing frozen artifact from <path>`

Bad:

- silently copying a SHA from memory without checking the cited artifact surface

### 2. Separate observed, inferred, and unverified

A clean header loses value if the body blurs what was actually observed versus what is a later interpretation.

### 3. Dirty worktrees need explicit wording

If the worktree is dirty, record that fact. If the artifact bytes still match `HEAD`, say that explicitly instead of treating all dirty states as the same problem.

### 4. Keep the non-authority boundary short and explicit

Examples:

- `Does not authorize runtime/default changes.`
- `Does not imply promotion or champion readiness.`
- `Historical reference only; not active execution guidance.`

## Intent

This template exists to reduce evidence-to-authority drift and weak provenance claims while keeping ordinary `RESEARCH` slices light. It is a helper surface, not a new SSOT or a new mandatory gate stack.
