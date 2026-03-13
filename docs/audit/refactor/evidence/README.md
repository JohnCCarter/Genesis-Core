# Refactor evidence index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying evidence artifacts.
For authoritative details, open the referenced markdown, transcript, manifest, diff, JSON, or TSV files directly.

## What lives here

This folder currently preserves supporting evidence for cleanup/refactor candidate work.
The observed file pattern includes:

- `*_implementation_report_*` — execution summaries for a candidate or batch
- `*_gate_transcript_*` and `*_raw_output_*` — gate and tool output captures
- `*_manifest_*`, `*_path_refcheck_*`, `*_refcheck_*` — scope and path/reference verification artifacts
- `*_pr_evidence_template_*` — PR-ready evidence summaries
- supporting `.json`, `.txt`, `.md`, `.tsv`, and `.diff` files for traceability

## Suggested reading order

1. Start with the candidate-specific `*_implementation_report_*` file if one exists.
2. Then read the matching gate transcript and manifest/refcheck artifacts.
3. Open raw outputs or diffs only when you need lower-level evidence.

## Interpretation note

Treat this folder as a supporting evidence archive.
The presence of a report or transcript does not by itself prove current repository state; verify against the paired command packet, signoff note, commit, or current workspace when needed.
