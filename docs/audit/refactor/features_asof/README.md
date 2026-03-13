# Features-asof refactor audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, open the packet and context-map files directly.

## What lives here

This folder currently contains slice-by-slice refactor records for the `features_asof` extraction campaign.
The file pattern is mainly:

- `command_packet_*` — per-slice scope and guardrails
- `context_map_*` — per-slice dependency/context mapping

## Suggested reading order

1. Start with the newest `command_packet_*` file if you need the latest slice context.
2. Read the matching `context_map_*` for file-level orientation.
3. If you need campaign history, work backward through earlier slice pairs.
4. For the broader extraction setup, open the non-slice `*_modul_split_*` documents.

## Interpretation note

Use this folder as a traceability index for the extraction campaign.
The newest files are usually the best orientation point, but they are not a substitute for reading the underlying documents themselves.
