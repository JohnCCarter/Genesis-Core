# Editor-worker customization drift inventory

## Claim header

- **Date:** `2026-05-15`
- **Branch:** `feature/evidence-closeout-pilot`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Concept` — why: this note inventories orchestration/customization seams only and does not authorize implementation or runtime behavior changes
- **Status:** `observational / seam inventory`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed`
- **Objective:** reduce the premortem risk of agent/governance sprawl by clarifying the currently visible editor-worker customization surfaces and the minimum dispatch discipline they imply
- **Baseline reference(s):** `artifacts/diagnostics/genesis_core_premortem_2026-05-15.md`, `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/QUICK_REF.md`
- **Representative surfaces reviewed:** `.github/agents/`, `.claude/agents/`, `.claude/QUICK_REF.md`, `/memories/repo/editor_worker_nested_worktrees_same_window.json`
- **Runtime base SHA:** `59c010c104903e49552608c15815aba1b9fa8fc3`
- **Evidence commit SHA:** `59c010c104903e49552608c15815aba1b9fa8fc3`
- **Working-tree status:** `clean at inventory start`
- **Config path:** `not applicable`
- **Config hash:** `not applicable`
- **Data-source policy:** `tracked repo customization surfaces and repo-scoped memory only`
- **Env flags:** `no additional env flags were set for this docs-only slice`
- **Artifact path:** `docs/analysis/diagnostics/editor_worker_customization_drift_inventory_2026-05-15.md`
- **What changed:** `one bounded inventory note records the current customization seams and the dispatch discipline they imply for future editor-worker slices`
- **What did not change:** `no agent file, instruction file, prompt file, or runtime surface changed`
- **Does not authorize:** `tooling rewrites, agent-registry consolidation, worker automation changes, or repo-governance precedence changes`

## Observed

### Visible repo-local agent surfaces are not symmetric across folders

The repo currently exposes different agent sets in two visible customization locations:

- `.github/agents/` contains:
  - `Codex53.agent.md`
  - `editor-slice-worker.agent.md`
  - `Opus46.agent.md`
  - `signoff-evidence-auditor.agent.md`
  - `slice-scout.agent.md`
  - `the-best-bug-finder-agent-in-the-universe.agent.md`
- `.claude/agents/` contains only:
  - `Codex53.agent.md`
  - `Opus46.agent.md`
  - `the-best-bug-finder-agent-in-the-universe.agent.md`

That means the repo-visible agent registry is already richer than the local `.claude` compatibility copy.

### Local quick-reference guidance already treats repo-local governance as primary

`.claude/QUICK_REF.md` explicitly states:

- every response starts with `Mode: <MODE> (source=<resolution reason>)`
- authority order is led by explicit user request, then `.github/copilot-instructions.md`, then `docs/OPUS_46_GOVERNANCE.md`, then `AGENTS.md`
- editor workers should default to bounded slices and explicit activation
- dedicated branch/worktree isolation is optional and must be explicit per worker/slice

This means the quick reference already points workers back toward repo-local governance and explicit dispatch rather than ambient inference.

Important boundary for this inventory:

- `QUICK_REF` is a Claude-local support surface and correctly belongs in `.claude/`
- the risk recorded here is **not** that `QUICK_REF` is misplaced
- the risk is that workers might assume all visible customization surfaces are symmetric or interchangeable when they are not

### Same-window worker worktrees are viable but not hard-isolation by default

The repo-scoped memory note `/memories/repo/editor_worker_nested_worktrees_same_window.json` records that:

- nested `.worktrees/ew-01..04` under the main checkout were successfully created
- `.worktrees/` was ignored via `.git/info/exclude`
- this supports same-window local worker isolation with stronger path discipline
- it does **not** create hard isolation automatically

### The premortem risk is therefore not hypothetical

The premortem explicitly ranked `Agent/governance sprawl creates inconsistent execution` as a real failure mode and named two concrete warning signals:

- overlapping writes from multiple workers
- stale or conflicting instruction sources causing convenience-first resolution

The currently visible customization topology is consistent with that risk: there are multiple valid surfaces, but they are not identical and therefore cannot be treated as interchangeable by default.

## Inferred

- Future editor-worker dispatch should treat `.github/agents/` and repo-local governance docs as the richer repo-local execution surface, while treating `.claude/**` as Claude-local support surfaces rather than as a guaranteed mirror.
- A worker launch should name its exact bounded slice, touched surface, and path/worktree assumptions explicitly instead of relying on ambient defaults like “same repo, same rules, same agent set”.
- When a slice depends on a repo-local specialist agent that exists only in `.github/agents/` (for example `editor-slice-worker`, `slice-scout`, or `signoff-evidence-auditor`), future dispatch should say so explicitly rather than assume parity with `.claude/agents/`.
- The same-window `.worktrees/` model is a valid future containment tool for overlapping or destructive work, but it should remain opt-in and recorded in the slice envelope rather than assumed globally.

## Unverified

- This slice does **not** prove which external toolchains currently prefer `.github/agents/` versus `.claude/agents/` at runtime.
- This slice does **not** prove that the observed asymmetry is harmful today; it proves only that the asymmetry exists and must be treated explicitly.
- This slice does **not** decide whether the long-term fix is consolidation, documentation only, or selective mirror refresh.

## Why this note matters

The premortem warned that Genesis-Core could fail by becoming correct locally but inconsistent operationally.

This is one of the cheapest places to reduce that risk:

- make the customization asymmetry visible
- force explicit worker dispatch instead of ambient inheritance
- keep worktree isolation an explicit tool rather than a fuzzy assumption

That is enough for one bounded slice. It improves future slice hygiene without pretending that a tooling rewrite is already justified.

## Bottom line

The first post-closeout workshop slice should treat editor-worker customization drift as a real but bounded coordination risk. `QUICK_REF` is correctly placed in `.claude/`, while the current repo-local agent/governance surface remains richer than the local Claude support copy. Same-window nested worktrees are viable but optional. Future autonomous slices should therefore record agent choice, touched surface, and worktree path explicitly instead of assuming that all visible customization surfaces are symmetric or automatically aligned.
