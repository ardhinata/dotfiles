#!/usr/bin/env bash
# Idempotent post-apply hook: ensure ~/.local/share/ exists for the shellx store,
# and keep the store files private.
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

  # The master key file holds the shellx master key. It is rendered by
  # chezmoi with mode 0600. The check keeps the mode after a manual copy.
  KEY_FILE="${HOME}/.local/share/shellx/master.key"
  if [ -f "${KEY_FILE}" ]; then
    chmod 600 "${KEY_FILE}"
  fi

  # Stale bytecode from the pre-1.6.0 deployment embeds the master key.
  # The current helpers keep no secret in their source, so their bytecode
  # is harmless. The two files below belong to helpers that no longer
  # exist in that shape.
  PYCACHE="${HOME}/.shell/helper/__pycache__"
  if [ -d "${PYCACHE}" ]; then
    find "${PYCACHE}" -maxdepth 1 -type f \
      \( -name 'shellxcpython-*.pyc' -o -name 'shellx_completion_helpercpython-*.pyc' \) \
      -delete
  fi
} 2>&1
exit 0
