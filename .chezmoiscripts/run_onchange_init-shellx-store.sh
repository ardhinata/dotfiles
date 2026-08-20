#!/usr/bin/env bash
# Idempotent post-apply hook: ensure ~/.local/share/ exists for the shellx store.
# Re-runs only when this file changes (chezmoi's run_onchange_ behavior).
set -euo pipefail
{
  echo "[chezmoiscript] BEGIN $(date -Iseconds)"
  PARENT="${HOME}/.local/share"
  mkdir -p "${PARENT}"
  chmod 700 "${PARENT}"

  MARKER="${HOME}/.shellx-store"
  if [ -f "${MARKER}" ]; then
    STORE="$(cat "${MARKER}")"
    if [ -d "${STORE}" ]; then
      chmod 700 "${STORE}"
      if [ -f "${STORE}/.sl" ]; then chmod 600 "${STORE}/.sl"; fi
      if [ -f "${STORE}/.idx" ]; then chmod 600 "${STORE}/.idx"; fi
      find "${STORE}" -maxdepth 1 -type f ! -name '.sl' ! -name '.idx' -exec chmod 600 {} +
    fi
  fi

  # Legacy shared-context wrapper cleanup (2026-08-20: merged kilo-shared-save ->
  # kilo-shared). Idempotent — no-op when legacy deploys are already gone.
  WRAPPER_BIN_DIR="${HOME}/.local/share/kilo/bin"
  if [ -e "${WRAPPER_BIN_DIR}/kilo-shared-save" ]; then
    rm -f "${WRAPPER_BIN_DIR}/kilo-shared-save"
  fi
  if [ -e "${WRAPPER_BIN_DIR}/kilo-shared-pull" ]; then
    rm -f "${WRAPPER_BIN_DIR}/kilo-shared-pull"
  fi
} 2>&1
exit 0
