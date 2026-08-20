#!/bin/sh
# kilo-shared — merged CLI for the per-project shared context repo (.tmp/docs/).
#
# Subcommands:
#   save "<msg>"       — commit staged changes (was: kilo-shared-save)
#   pull [remote] [branch] — fetch in .tmp/docs/ (was: kilo-shared-pull)
#   detect <name>      — print resolved install path of a wrapper (agent-only)
#   init [--here] [--force] — bootstrap the shared context repo (bare + clone + hook)
#   --version | -v     — print wrapper version
#   --help | -h        — print this help
#
# The wrapper itself is NOT on $PATH by default; users prepend
# ~/.local/share/kilo/bin to PATH or invoke by absolute path.
# Agent rules may call `kilo-helper-shared-detect` for a single decision
# helper that mirrors spec-kit's check_tool two-tier logic.

set -e

KILO_SHARED_VERSION="0.2.0"
WRAPPER_BIN_DIR="$HOME/.local/share/kilo/bin"

# kilo_shared_resolve_path — single source of truth for the .tmp/docs/ path.
# Priority: $KILO_SHARED_CONTEXT_PATH env var → git rev-parse from $PWD.
# Echoes the absolute path on stdout. Exits non-zero with a clear message
# on stderr if neither yields a valid .tmp/docs/ directory.
kilo_shared_resolve_path() {
  if [ -n "$KILO_SHARED_CONTEXT_PATH" ] && [ -d "$KILO_SHARED_CONTEXT_PATH" ]; then
    printf '%s\n' "$KILO_SHARED_CONTEXT_PATH"
    return 0
  fi
  PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "kilo-shared: not in a git repo and KILO_SHARED_CONTEXT_PATH unset." >&2
    echo "  Run from inside the project, or set KILO_SHARED_CONTEXT_PATH explicitly." >&2
    return 2
  }
  if [ -d "$PROJECT_ROOT/.tmp/docs" ]; then
    printf '%s\n' "$PROJECT_ROOT/.tmp/docs"
    return 0
  fi
  echo "kilo-shared: $PROJECT_ROOT/.tmp/docs does not exist." >&2
  echo "  Run 'kilo-shared init --here' to bootstrap." >&2
  return 2
}

usage() {
  cat <<'EOF'
kilo-shared — merged CLI for the per-project shared context repo (.tmp/docs/).

Usage:
  kilo-shared save "<message>"          commit staged changes
  kilo-shared pull [remote] [branch]   fetch in .tmp/docs/ (default: origin main)
  kilo-shared detect <name>            print resolved install path
  kilo-shared init [--here] [--force]  bootstrap shared context repo
  kilo-shared --version | -v           print wrapper version
  kilo-shared --help | -h              print this help

Wrapper lives at ~/.local/share/kilo/bin/kilo-shared (NOT on $PATH by default).
EOF
}

cmd_save() {
  MSG="${1:-auto: shared-context capture}"
  DOCS_PATH=$(kilo_shared_resolve_path)
  cd "$DOCS_PATH"

  git add -A

  if git diff --cached --quiet; then
    echo "kilo-shared save: nothing staged; skipping commit."
    exit 0
  fi

  git commit -m "$MSG"
  echo "kilo-shared save: committed with message: $MSG"
  git log -1 --oneline
}

cmd_pull() {
  REMOTE="${1:-origin}"
  BRANCH="${2:-main}"
  DOCS_PATH=$(kilo_shared_resolve_path)
  cd "$DOCS_PATH"

  if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
    echo "kilo-shared pull: shared context has no '$REMOTE' remote." >&2
    echo "  Either add one:" >&2
    BARE_REPO=$(git rev-parse --git-common-dir 2>/dev/null)
    echo "    git -C \"$BARE_REPO\" remote add $REMOTE <url>" >&2
    echo "  Or skip cross-worktree collision checks." >&2
    exit 2
  fi

  git fetch "$REMOTE" "$BRANCH"
}

cmd_detect() {
  NAME="${1:-kilo-shared}"
  # Delegate to the helper when present; fallback to inline tier-1 check.
  HELPER="$WRAPPER_BIN_DIR/kilo-helper-shared-detect"
  if [ -x "$HELPER" ]; then
    "$HELPER" "$NAME"
    return $?
  fi
  if [ -x "$WRAPPER_BIN_DIR/$NAME" ]; then
    printf '%s\n' "$WRAPPER_BIN_DIR/$NAME"
    return 0
  fi
  ASSET="$HOME/.local/share/chezmoi/dot_config/kilo/exact_skills/shared-context/assets/${NAME}.sh"
  if [ -f "$ASSET" ]; then
    echo "$NAME not installed. Run: chezmoi apply" >&2
  else
    echo "$NAME asset missing at $ASSET" >&2
  fi
  return 1
}

cmd_init() {
  HERE=0
  FORCE=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --here) HERE=1 ;;
      --force) FORCE=1 ;;
      *) echo "kilo-shared init: unknown flag $1" >&2; exit 2 ;;
    esac
    shift
  done

  if [ "$HERE" -eq 1 ]; then
    PROJECT_ROOT="$(pwd)"
  else
    PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
      echo "kilo-shared init: not in a git repo; pass --here and re-run from the project root." >&2
      exit 2
    }
  fi

  INIT_SCRIPT="$HOME/.local/share/kilo/bin/kilo-shared-init.sh"
  if [ ! -x "$INIT_SCRIPT" ]; then
    INIT_SCRIPT="$(dirname "$0")/kilo-shared-init.sh"
    if [ ! -x "$INIT_SCRIPT" ]; then
      INIT_SCRIPT="$HOME/.local/share/chezmoi/dot_config/kilo/exact_skills/shared-context/assets/kilo-shared-init.sh"
    fi
  fi
  if [ ! -x "$INIT_SCRIPT" ]; then
    echo "kilo-shared init: kilo-shared-init.sh not found; run chezmoi apply." >&2
    exit 2
  fi

  KILO_SHARED_INIT_PROJECT_ROOT="$PROJECT_ROOT" KILO_SHARED_INIT_FORCE="$FORCE" \
    "$INIT_SCRIPT"
}

case "${1:-}" in
  save) shift; cmd_save "$@" ;;
  pull) shift; cmd_pull "$@" ;;
  detect) shift; cmd_detect "$@" ;;
  init) shift; cmd_init "$@" ;;
  --version|-v) printf 'kilo-shared %s\n' "$KILO_SHARED_VERSION" ;;
  --help|-h|"") usage ;;
  *)
    echo "kilo-shared: unknown subcommand: $1" >&2
    usage >&2
    exit 2
    ;;
esac
