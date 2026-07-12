#!/usr/bin/env bash
# Idempotent post-apply hook: ensure ~/.local/share/ exists for the shellx store.
# Re-runs only when this file changes (chezmoi's run_onchange_ behavior).
set -euo pipefail

PARENT="${HOME}/.local/share"
mkdir -p "${PARENT}"
chmod 700 "${PARENT}"

# If shellx has been initialized, refresh permissions on the slug directory.
MARKER="${HOME}/.shellx-store"
if [[ -f "${MARKER}" ]]; then
  STORE="$(cat "${MARKER}")"
  if [[ -d "${STORE}" ]]; then
    chmod 700 "${STORE}"
    [[ -f "${STORE}/.sl" ]] && chmod 600 "${STORE}/.sl"
    [[ -f "${STORE}/.idx" ]] && chmod 600 "${STORE}/.idx"
    find "${STORE}" -maxdepth 1 -type f ! -name '.sl' ! -name '.idx' -exec chmod 600 {} +
  fi
fi