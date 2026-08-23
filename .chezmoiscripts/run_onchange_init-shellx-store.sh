#!/usr/bin/env bash
# Idempotent post-apply hook: ensure ~/.local/share/ exists for the shellx store,
# and bytecode-compile the deployed shellx for fast cold start.
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

  # Bytecode-compile the deployed shellx so subsequent Python starts reuse
  # the parsed AST (saves ~20–30 ms on cold start). Pycache is written
  # under __pycache__/ next to the script; .chezmoiignore already excludes
  # that pattern, so it never gets re-deployed or checked in.
  SHELLX_DEPLOY="${HOME}/.shell/helper/shellx"
  if [ -f "${SHELLX_DEPLOY}" ]; then
    python3 -m py_compile "${SHELLX_DEPLOY}" 2>/dev/null || true
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
