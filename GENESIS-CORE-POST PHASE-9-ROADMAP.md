📦 GENESIS-CORE — POST PHASE 9 ROADMAP
Scope: Edge Origin Isolation & Structural Attribution
🧾 0. VERIFIED BASELINE (LOCKED CONTEXT)
Observed (från artifacts)
Phase 6–7 → signal layer invalidated
Phase 8 → candidates discovered (NOT validated)
Phase 9 → edge is not state-dependent
Determinism: PASS (hash match)
Governance invariant
❌ NO signal redesign
❌ NO feature engineering
❌ NO parameter tuning
❌ NO Optuna
✅ Artifact-only analysis
✅ Deterministic pipelines
✅ Fail-closed
🎯 1. OBJECTIVE (STRICT)
Primary goal

Identify where edge originates in the system

NOT:

what predicts it
what correlates with it
Formal definition

Edge origin ∈:

Execution layer
Sizing layer
Trade lifecycle / path
Selection / admission
Emergent / non-local effects
🚨 2. HARD CONSTRAINTS

Copilot MUST enforce:

Determinism across runs (hash equality)
EXACT trade mapping (1:1 join)
No mutation of:
strategy logic
signals
config
All outputs must be reproducible artifacts
🧱 PHASE 10 — EDGE ORIGIN ISOLATION
🎯 Goal

Decompose total edge into mechanistic contributors

🔹 10.1 Execution Attribution
Task

Split PnL into:

entry quality
exit quality
Implementation

Artifacts:

execution_attribution.json
execution_summary.md

Metrics:

MAE (max adverse excursion)
MFE (max favorable excursion)
realized vs unrealized edge
Required analysis
Compare:
actual exits vs hypothetical fixed exits
actual entries vs randomized entries (time-shifted)
🔹 10.2 Sizing Attribution
Task

Measure edge contribution from sizing

Implementation

Artifacts:

sizing_attribution.json
sizing_summary.md

Analysis:

normalize all trades → unit size
recompute PF / expectancy
compare vs actual
Output
edge contribution from sizing = Δ(expectancy)
🔹 10.3 Trade Lifecycle / Path Dependency
Task

Determine if edge depends on sequence

Implementation

Artifacts:

path_dependency.json
path_summary.md

Tests:

shuffle trade order
preserve trades but randomize sequence
recompute equity curve
Interpretation
If PF changes → path-dependent edge
🔹 10.4 Admission / Selection Attribution
Task

Test if which trades are taken creates edge

Implementation

Artifacts:

selection_attribution.json
selection_summary.md

Tests:

random subset sampling (same N trades)
compare PF vs actual selection
🔹 10.5 Counterfactual Engine
Task

Run controlled perturbations

Required experiments
random entry timing
fixed exits
inverted signals (control test)
Output
counterfactual_matrix.json
🔹 Phase 10 Completion Criteria

Must produce:

All attribution artifacts
Determinism proof
No governance violations
🔹 Phase 10 Expected Outcomes
Possible:
Edge = execution-driven
Edge = sizing-driven
Edge = selection-driven
Edge = path-dependent
Edge = unresolved
🧠 PHASE 11 — EDGE STABILITY & GENERALIZATION
🎯 Goal

Test if edge survives perturbation of environment

🔹 11.1 Temporal Stability
split dataset into:
early / mid / late
recompute metrics
🔹 11.2 Bootstrap / Resampling
resample trades with replacement
compute distribution of PF / expectancy
🔹 11.3 Sensitivity Analysis
small perturbations:
price noise
latency shifts
observe edge stability
🔹 Outputs
edge_stability.json
bootstrap_distribution.json
🔹 Completion Criteria
Edge classified as:
stable
fragile
noise-driven
🔬 PHASE 12 — EDGE MINIMALITY
🎯 Goal

Find minimal system that preserves edge

🔹 Tasks
progressively remove:
components
filters
conditions
🔹 Method
ablation (but system-level, not feature-level)
🔹 Output
minimal_system.json
ablation_summary.md
🔹 Interpretation
if edge survives removal → redundant complexity
if edge collapses → critical component identified
🧩 PHASE 13 — EDGE CLASSIFICATION
🎯 Goal

Classify edge type

Possible classes
structural (market microstructure)
statistical artifact
regime-independent drift
execution inefficiency
emergent system behavior
Output
edge_classification.md
🚫 3. GLOBAL STOP CONDITIONS

Pipeline must STOP if:

determinism breaks
join integrity fails
sample size becomes invalid
governance violated
📦 4. FINAL DELIVERABLE

After Phase 13:

Produce:

EDGE_ORIGIN_REPORT.md

Must include:

origin hypothesis
evidence
falsification attempts
residual uncertainty
🧠 META (IMPORTANT FOR COPILOT)
Inferred (explicit)

From Phase 6–9:

Edge is NOT explained by:

signals
features
states
Therefore:

Edge is likely:

systemic
emergent
non-local

Copilot MUST:

avoid returning to signal-space
avoid feature expansion
focus ONLY on system behavior
