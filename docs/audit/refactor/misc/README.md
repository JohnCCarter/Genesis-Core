# Misc refactor audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, open the individual packet or context-map files directly.

## What lives here

This folder currently groups refactor records that do not appear to belong to a larger dedicated campaign folder.
The observed file pattern includes:

- `command_packet_*` — task-specific scope and guardrails
- `context_map_*` — local dependency and risk mapping for a specific task

## Suggested reading order

1. Open the `command_packet_*` file for the task you are investigating.
2. Read the matching `context_map_*` file if one exists.
3. Treat other files in this folder as neighboring but independent traceability records.

## Interpretation note

Because this is a mixed folder, avoid assuming a single shared status across all files.
Read each document as an individual record unless a file explicitly states a broader grouping.
