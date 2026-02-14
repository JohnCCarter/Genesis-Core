#!/usr/bin/env bash
set -euo pipefail

SRC_REPO="${GENESIS_SRC_REPO:-/home/azureuser/Genesis-Core}"
DST_REPO="${GENESIS_DST_REPO:-/opt/genesis/Genesis-Core}"

DRY_RUN=0
RESTART=1
REGENERATE_ENV=1
CAPTURE_RC=1

usage() {
	cat <<'EOF'
Usage: deploy_home_to_opt.sh [options]

One-command deploy from /home workspace to /opt runtime tree on genesis-we.

Options:
	--dry-run        Show rsync changes only (no writes, no restarts)
	--no-restart     Skip systemctl daemon-reload + restart
	--no-env         Skip .env -> .env.systemd regeneration in /opt
	--no-rc          Skip post-restart RC diagnostics capture
	-h, --help       Show this help

Environment overrides:
	GENESIS_SRC_REPO  (default: /home/azureuser/Genesis-Core)
	GENESIS_DST_REPO  (default: /opt/genesis/Genesis-Core)
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--dry-run)
			DRY_RUN=1
			shift
			;;
		--no-restart)
			RESTART=0
			shift
			;;
		--no-env)
			REGENERATE_ENV=0
			shift
			;;
		--no-rc)
			CAPTURE_RC=0
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "[deploy] unknown option: $1" >&2
			usage >&2
			exit 2
			;;
	esac
done

require_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "[deploy] missing command: $1" >&2
		exit 1
	}
}

for c in git rsync; do
	require_cmd "$c"
done

if (( RESTART == 1 )); then
	require_cmd systemctl
	require_cmd curl
	require_cmd ss
fi

[[ -d "$SRC_REPO" ]] || {
	echo "[deploy] source repo not found: $SRC_REPO" >&2
	exit 1
}
[[ -d "$DST_REPO" ]] || {
	echo "[deploy] destination repo not found: $DST_REPO" >&2
	exit 1
}

echo "[deploy] src=$SRC_REPO"
echo "[deploy] dst=$DST_REPO"
echo "[deploy] src head: $(git -C "$SRC_REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "[deploy] dst head: $(git -C "$DST_REPO" rev-parse --short HEAD 2>/dev/null || echo unknown)"

RSYNC_ARGS=(
	-a
	--delete
	--exclude .git
	--exclude .venv
	--exclude '__pycache__'
	--exclude '*.pyc'
	--exclude '*.pyo'
	--exclude '*.egg-info'
	--exclude logs
	--exclude results
	--exclude data
	--exclude .env
	--exclude .env.systemd
	--exclude .nonce_tracker.json
	--exclude dev.overrides.local.json
	--exclude '*MARKER.txt'
)

if (( DRY_RUN == 1 )); then
	echo "[deploy] dry-run enabled"
	rsync "${RSYNC_ARGS[@]}" --itemize-changes --dry-run "$SRC_REPO/" "$DST_REPO/"
	exit 0
fi

echo "[deploy] syncing files..."
rsync "${RSYNC_ARGS[@]}" "$SRC_REPO/" "$DST_REPO/"
echo "[deploy] sync complete"

if (( REGENERATE_ENV == 1 )); then
	GEN_SCRIPT="$DST_REPO/scripts/generate_env_systemd.sh"
	if [[ -x "$GEN_SCRIPT" && -f "$DST_REPO/.env" ]]; then
		echo "[deploy] regenerating .env.systemd"
		"$GEN_SCRIPT" "$DST_REPO/.env" "$DST_REPO/.env.systemd"
	else
		echo "[deploy] skipping env regeneration (missing script or .env)"
	fi
fi

if (( RESTART == 1 )); then
	echo "[deploy] daemon-reload + restart services"
	sudo systemctl daemon-reload
	sudo systemctl restart genesis-paper genesis-runner
	sleep 2

	echo "[deploy] verify genesis-paper"
	systemctl show genesis-paper \
		-p ActiveState -p SubState -p MainPID -p NRestarts -p WorkingDirectory --no-pager

	echo "[deploy] verify genesis-runner"
	systemctl show genesis-runner \
		-p ActiveState -p SubState -p MainPID -p NRestarts -p WorkingDirectory --no-pager

	echo "[deploy] verify env file source"
	systemctl show genesis-paper -p EnvironmentFiles -p DropInPaths --no-pager

	echo "[deploy] verify listener + health"
	ss -ltnp | grep ':8000 ' || true
	curl -fsS http://127.0.0.1:8000/health || true

		if (( CAPTURE_RC == 1 )); then
			RC_SCRIPT="$DST_REPO/scripts/capture_paper_rc.sh"
			if [[ -x "$RC_SCRIPT" ]]; then
				echo "[deploy] capture RC diagnostics"
				"$RC_SCRIPT" --window-minutes 30 || echo "[deploy] warning: RC capture failed"
			else
				echo "[deploy] skip RC capture (script missing: $RC_SCRIPT)"
			fi
		fi
fi

echo "[deploy] done"
