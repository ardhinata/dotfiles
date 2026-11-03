#!/usr/bin/env bash
# Start the local embeddings proxy with the service manager of this OS.
#
# Runs on every chezmoi apply. It starts the service when the service is
# not running and leaves a healthy one alone. The proxy holds no state, so
# a restart is cheap, but a restart during an apply opens a short window
# where an embedding call fails. Restart the service by hand after you
# change the unit or the plist.
#
# Needs no root rights.

set -uo pipefail

LABEL="com.user.embedding-dimensions-proxy"
UNIT="embedding-dimensions-proxy.service"

warn() { printf '[embeddings-proxy] %s\n' "$*" >&2; }

case "$(uname -s)" in
	Linux)
		systemctl --user daemon-reload >/dev/null 2>&1 \
			|| warn "systemd daemon-reload failed"
		systemctl --user enable --now "${UNIT}" >/dev/null 2>&1 \
			|| warn "could not start ${UNIT}; run: systemctl --user start ${UNIT}"
		;;
	Darwin)
		uid="$(id -u)"
		mkdir -p "${HOME}/.local/state/embedding-dimensions-proxy" \
			|| warn "could not create the log directory"
		if launchctl print "gui/${uid}/${LABEL}" >/dev/null 2>&1; then
			:
		else
			launchctl bootstrap "gui/${uid}" \
				"${HOME}/Library/LaunchAgents/${LABEL}.plist" >/dev/null 2>&1 \
				|| warn "could not load ${LABEL}; run: launchctl bootstrap gui/${uid} ${HOME}/Library/LaunchAgents/${LABEL}.plist"
		fi
		;;
esac

exit 0
