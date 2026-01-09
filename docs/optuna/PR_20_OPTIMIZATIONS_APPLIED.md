# PR #20 Optimizations Applied

**Date:** 2025-11-21
**Status:** Applied locally

## Overview

The optimizations from PR #20 "Optimize Optuna integration hot paths" have been manually applied to the local codebase. These changes aim to improve the performance of the Optuna optimization loop by 2-3x.

## Changes Applied

### 1. SQLite Optimizations (`src/core/utils/optuna_helpers.py`)

- Enabled `WAL` (Write-Ahead Logging) mode for better concurrency.
- Set `synchronous=NORMAL` for faster writes while maintaining safety in WAL mode.
- Increased `cache_size` to 10MB.
- Set `temp_store=MEMORY` to avoid disk I/O for temporary tables.
- Increased `page_size` to 16KB.

### 2. JSON Parsing (`src/core/optimizer/runner.py`)

- Added optional support for `orjson` (fast JSON parser).
- Implemented `_json_loads` helper to use `orjson` if available, falling back to `json`.
- Updated `_load_existing_trials` to use `_json_loads`.

### 3. Trial Key Generation (`src/core/optimizer/runner.py`)

- Optimized `_trial_key` to use a "fast path":
  - Tries to dump `params` directly to JSON first.
  - Only falls back to `canonicalize_config` if serialization fails.
  - Returns SHA256 digest directly (instead of JSON string) for faster dictionary lookups.
- Added cache trimming (LRU approximation) to prevent memory leaks.

### 4. Deep Merge (`src/core/optimizer/runner.py`)

- Replaced recursive `_deep_merge` with an iterative stack-based implementation.
- Eliminates recursion depth limits and reduces function call overhead.

### 5. Value Expansion (`src/core/optimizer/runner.py`)

- Optimized `_expand_value` and `_clone_value`.
- Uses `type()` checks instead of `isinstance()` for primitive types (int, float, str, bool, None) for speed.
- Explicitly handles `list` and `dict` cloning to avoid `copy.deepcopy` overhead.

### 6. Parameter Suggestion (`src/core/optimizer/runner.py`)

- Verified `_suggest_parameters` uses cached decimal calculations for float steps.

## Verification

- `python -c "from core.optimizer.runner import _trial_key"` runs successfully.
- Code structure matches the PR description and diff.
