#!/usr/bin/env bash
set -euo pipefail

URL="${WAIT_FOR_PAPER_URL:-http://127.0.0.1:8000/health}"
TIMEOUT_SECONDS="${WAIT_FOR_PAPER_TIMEOUT_SECONDS:-60}"
SLEEP_SECONDS="${WAIT_FOR_PAPER_INTERVAL_SECONDS:-2}"

start_ts=$(date +%s)

while true; do
  if curl -fsS --max-time 2 "$URL" >/dev/null; then
    echo "[wait_for_paper] API ready: $URL"
    exit 0
  fi

  now_ts=$(date +%s)
  elapsed=$((now_ts - start_ts))
  if (( elapsed >= TIMEOUT_SECONDS )); then
    echo "[wait_for_paper] timeout after ${TIMEOUT_SECONDS}s waiting for $URL" >&2
    exit 1
  fi

  sleep "$SLEEP_SECONDS"
done
