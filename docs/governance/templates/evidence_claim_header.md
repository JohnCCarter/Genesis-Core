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

- branch
- authority level
- claim status (`observed`, `inferred`, `unverified`)
- checkout scope / portability label when reproducibility or portability meaning is in play
- runtime base SHA
- evidence commit SHA, or an explicit note that the current slice did not rerun the evidence
- input carrier
- working-tree clean/dirty status
- data-source policy
- relevant env flags
- cache policy
- config path and hash when relevant
- symbol/timeframe/window/warmup when relevant
- symbol mode
- artifact path(s) and hash(es) when generated or cited
- a short `does not authorize` boundary

## Mandatory minimum for decision-influencing evidence

When a note is likely to influence a later packet, review, carrier decision, or runtime-adjacent discussion, the claim header must name at minimum:

- `Branch`
- `Runtime base SHA`
- `Evidence commit SHA` or explicit non-rerun wording
- `Checkout scope / portability label` when the note makes reproducibility or portability claims
- `Working-tree status`
- `Input carrier`
- `Data-source policy`
- `Env flags`
- `Cache policy`
- `Authority level`
- `Does not authorize`

`Config path` and `Config hash` remain required whenever the note depends on config-bearing meaning.

## Quick scope reference for `observed` claims

When `Claim status: observed` is doing reproducibility or portability work, do not leave the checkout scope implicit.

These labels describe the portability boundary of the claim, not its strength, quality, or authority level.

Use one of these labels explicitly when they fit:

- **`same-local-checkout only`**
  - observed on this exact working state only
  - portability stops at this checkout/workstation surface
  - pair it with `Working-tree status`, `Evidence commit SHA` or explicit non-rerun wording, and the exact `Input carrier`
- **`fixture-level`**
  - observed from one tracked fixture or other narrow commit-safe carrier only
  - do not let this drift into broader replay or clean-checkout portability language
  - pair it with the exact fixture/carrier path under `Input carrier`
- **`historical-trace-level`**
  - observed from one fixed retained historical trace, bundle, or frozen root
  - portability remains tied to that retained carrier, not to a fresh full-chain rerun
  - pair it with the exact retained carrier/root under `Input carrier`
- **`full-chain clean-checkout-level`**
  - use only when a clean checkout can regenerate the named claim-bearing chain from tracked inputs under the stated envelope

If none of these labels fit because the note is concept-only, planning-only, or historical-reference-only, say that explicitly instead of implying a portability level.

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
- **Checkout scope / portability label:**
- **Objective:**
- **Baseline reference(s):**
- **Candidate / comparison surface:**
- **Input carrier:**
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

### 5. Name the input carrier explicitly for decision-bearing notes

`Input carrier` should name the exact surface the note depends on, for example:

- one tracked fixture path
- one exact historical artifact path or root
- one retained bundle pointer
- one summary artifact when the note is summary-only by construction

## Intent

This template exists to reduce evidence-to-authority drift and weak provenance claims while keeping ordinary `RESEARCH` slices light. It is a helper surface, not a new SSOT or a new mandatory gate stack.
