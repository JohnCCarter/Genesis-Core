# Shard C Breadth Refactor Audit (2026-03-06)

Scope: `src/core/**` + `mcp_server/**`

## 1) Inventory evidence

- Total tracked files in scope: **117**
- Tracked Python files in scope: **112**
- Area distribution:
  - `src/core/strategy`: 30
  - `src/core/utils`: 17
  - `src/core/indicators`: 11
  - `src/core/io`: 9
  - `mcp_server`: 9
  - `src/core/backtest`: 8
  - `src/core/config`: 8
  - `src/core/ml`: 8
  - `src/core/optimizer`: 6
  - remaining areas: 11

## 2) Staged discovery tools run

Artifacts under `logs/audit/shard_c_breadth_2026-03-06/`:

- `jscpd/jscpd-report.json`
- `radon_cc.json`
- `vulture.txt`
- `semgrep.json` + `semgrep.stderr.log`
- `importlinter.ini` + `importlinter.txt`
- `ast_structural_scan.json`
- `summary.txt`

Key outputs:

- JSCPD duplicates: **14** blocks (10 intra-file, 4 inter-file)
- Radon complexity hotspots: **84 C-rank entities**, **0 D/E/F**
- Vulture high-confidence findings: **1** (`mcp_server/server.py:80`)
- Semgrep (`p/python`): **0 findings**
- Import-linter contracts: **2 kept, 0 broken**
  - core <-> mcp_server independence: KEPT
  - core.io not importing core.server surfaces: KEPT

## 3) Candidate families and classification

### Family A — Duplicated helper logic (already refactored)

- Evidence: prior candidate commits in this branch.
- Classification: **REFACTOR (DONE)**
- Scope completed:
  - `src/core/io/bitfinex/read_helpers.py` dedupe + tests
  - `mcp_server/server.py`, `mcp_server/remote_server.py`, `mcp_server/utils.py` shared redaction helper + tests
  - `src/core/strategy/features_asof.py` local safe-value helper dedupe in hash path

### Family B — Duplicate implementations in websocket readers

- Evidence: JSCPD blocks #1-4 (`ws_public.py` intra + `ws_auth.py` vs `ws_public.py`)
- Classification: **KEEP**
- Reason: live websocket flow/state/timing surfaces; safe extraction is not invariant-clear from breadth scan and must fail-closed.

### Family C — Duplicate implementations in ML labeling (`labeling.py` vs `labeling_fast.py`)

- Evidence: JSCPD block #6 (45 lines cross-file)
- Classification: **ALLOWLIST**
- Reason: intentional parity between Python and optimized/Numba paths; dedupe risks coupling performance implementation with reference behavior.

### Family D — Local duplication in high-sensitivity backtest engines

- Evidence: JSCPD blocks #10-14 in `trade_logger.py` and `htf_exit_engine.py`
- Classification: **KEEP**
- Reason: high-sensitivity zone (`src/core/backtest/*`); duplication appears branch-specific decision logic where extraction may alter determinism/readability under edge cases.

### Family E — Indicator boilerplate duplication (`adx.py` vs `atr.py`)

- Evidence: JSCPD blocks #7-8
- Classification: **KEEP**
- Reason: small and readable local guards; extraction benefit low and introduces shared dependency for minimal gain.

### Family F — Local complexity hotspots

- Evidence: Radon C-rank concentration in `optimizer/runner.py`, `backtest/engine.py`, `mcp_server/tools.py`, strategy components
- Classification: **KEEP**
- Reason: no D/E/F severity; broad refactor would be non-narrow and behavior-risky.

### Family G — Wrapper-heavy call chains / internal indirection

- Evidence: AST structural scan reports 8 thin wrappers (top: `core/config/authority.py`, `core/server.py`)
- Classification: **ALLOWLIST**
- Reason: wrappers are mostly explicit boundary seams/compatibility APIs and improve intent clarity.

### Family H — Naming inconsistency clusters

- Evidence: AST scan found 3 private class names (`_CacheEntry`, `_MCPStub`, `_RemoteTokenMiddleware`)
- Classification: **ALLOWLIST**
- Reason: consistent private-class naming pattern, not a harmful inconsistency cluster.

### Family I — Safe local control-flow simplification

- Evidence: Vulture 1 finding (`mcp_server/server.py:80` unreachable after raise)
- Classification: **KEEP**
- Reason: this is inside `@asynccontextmanager` fallback; sentinel `yield` keeps async-generator shape and should not be removed blindly.

## 4) Summary decision for Shard C

Decision basis requires candidates to be narrow, behavior-preserving, architecture-safe, and invariant-safe.

- Broad shard audit has been executed with staged tooling across full scope.
- Major families were classified with fail-closed policy.
- No unresolved **major high-signal + clearly safe** structural opportunities remain from this breadth pass.

Conclusion: **Shard C can be considered structurally complete from breadth-first refactor-audit perspective**.
