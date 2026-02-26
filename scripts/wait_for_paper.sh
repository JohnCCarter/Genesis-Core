#!/usr/bin/env bash
echo "[DEPRECATED] scripts/wait_for_paper.sh moved to scripts/archive/2026-02/analysis/wait_for_paper.sh." >&2
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/archive/2026-02/analysis/wait_for_paper.sh"
exec bash "${TARGET}" "$@"
