#!/usr/bin/env bash
echo "[DEPRECATED] scripts/capture_paper_rc.sh moved to scripts/archive/2026-02/analysis/capture_paper_rc.sh." >&2
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/archive/2026-02/analysis/capture_paper_rc.sh"
exec bash "${TARGET}" "$@"
