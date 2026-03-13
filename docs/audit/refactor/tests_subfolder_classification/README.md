# Tests subfolder classification audit index

This README is a navigation aid for the files currently present in this folder.
It does not replace or reinterpret the underlying audit or evidence documents.
For authoritative details, read the plan and individual command packet files directly.

## What lives here

This folder preserves planning and execution records for the test-layout classification campaign.
The file pattern includes:

- `tests_subfolder_classification_plan_*` — overall campaign plan/reference
- `command_packet_tests_subfolder_classification_phase*` — phase-level batches
- `command_packet_tests_subfolder_classification_backtest_*` — backtest-focused moves
- `command_packet_tests_subfolder_classification_utils_*` — utils-focused moves

## Suggested reading order

1. Start with the newest `tests_subfolder_classification_plan_*` file.
2. Then read the relevant phase packet for the batch you care about.
3. Finally, open the specific `backtest_*` or `utils_*` packet for the exact migration candidate.

## Interpretation note

Treat these files as historical planning and execution records.
Do not assume that a packet alone proves current status for a test file; verify against the referenced move, commit, or current workspace state when needed.
