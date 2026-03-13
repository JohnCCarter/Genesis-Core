# Optimizer refactor audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, open the referenced command packet and context map files directly.

## What lives here

This folder currently holds optimizer refactor planning/evidence artifacts for the `runner.py` split work.
The file pattern in this folder is primarily:

- `command_packet_*` — scope, constraints, and gate expectations for a slice
- `context_map_*` — local context and file/symbol map for that slice

## Suggested reading order

1. Open the newest `command_packet_*` file first.
2. Open the matching `context_map_*` file next.
3. Read older packet/map pairs only when you need the history of a previous slice.

## Current observed subtopics

- split-2: Optuna orchestration / validation / promotion support
- split-3: config / metadata / parameter-space extraction

## Interpretation note

Treat these files as refactor traceability records for this folder.
Do not infer broader completion or approval status beyond what each individual packet or signoff document explicitly states.
