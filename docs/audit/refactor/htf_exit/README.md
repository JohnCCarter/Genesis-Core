# HTF-exit refactor audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, read the command packet and context map files directly.

## What lives here

This folder currently contains refactor records for the HTF exit engine split work.
The visible file pattern is:

- `command_packet_*` — scope, constraints, and expected gates for a slice
- `context_map_*` — local dependency, test, and risk mapping for that slice

## Suggested reading order

1. Open the newest `command_packet_*` file first.
2. Open the matching `context_map_*` file next.
3. Read earlier packet/map pairs only when you need the background for the previous slice.

## Interpretation note

Treat this folder as traceability material for the HTF-exit refactor workstream.
Do not infer broader completion or approval status beyond what each individual document explicitly states.
