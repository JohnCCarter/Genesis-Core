#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-/opt/genesis/Genesis-Core/.env}"
DST="${2:-/opt/genesis/Genesis-Core/.env.systemd}"

if [[ ! -f "$SRC" ]]; then
  echo "[env-systemd] source not found: $SRC" >&2
  exit 1
fi

umask 077
TMP="${DST}.tmp.$$"

# Keep values as-is but normalize encoding/line endings for systemd:
# - remove UTF-8 BOM on first line
# - remove CR from CRLF line endings
awk 'NR==1{sub(/^\xef\xbb\xbf/,"")} {sub(/\r$/,"")} {print}' "$SRC" > "$TMP"

mv "$TMP" "$DST"
chmod 600 "$DST"

echo "[env-systemd] generated: $DST"
