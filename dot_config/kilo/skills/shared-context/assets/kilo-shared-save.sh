#!/bin/sh
# kilo-shared-save — commit the current state of .tmp/docs/ to the shared context repo.
#
# Installed at ~/.local/share/kilo/bin/kilo-shared-save by .kilo/setup-script.
# Usage: kilo-shared-save "<short-message>"
#
# Path discovery (in priority order):
#   1. $KILO_SHARED_CONTEXT_PATH env var (set by the agent's environment)
#   2. git rev-parse --show-toplevel from $PWD, then append .tmp/docs
#
# This wrapper exists so the agent has a single command to invoke after every
# write to .tmp/docs/{notes,plans,postmortems,user_cache}/. It is the
# enforcement point for the "every write must commit" rule.

set -e

if [ -z "$KILO_SHARED_CONTEXT_PATH" ]; then
  PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "kilo-shared-save: not in a git repo and KILO_SHARED_CONTEXT_PATH unset." >&2
    echo "  Run from inside the project, or set KILO_SHARED_CONTEXT_PATH explicitly." >&2
    exit 2
  }
  KILO_SHARED_CONTEXT_PATH="$PROJECT_ROOT/.tmp/docs"
fi

if [ ! -d "$KILO_SHARED_CONTEXT_PATH" ]; then
  echo "kilo-shared-save: $KILO_SHARED_CONTEXT_PATH does not exist." >&2
  echo "  Run .kilo/setup-script first." >&2
  exit 2
fi

MSG="${1:-auto: shared-context capture}"

cd "$KILO_SHARED_CONTEXT_PATH"

# Stage everything; pre-commit hook blocks scratch/ paths.
git add -A

# Skip if nothing is staged (avoids empty-commit rejection by the hook).
if git diff --cached --quiet; then
  echo "kilo-shared-save: nothing staged; skipping commit."
  exit 0
fi

git commit -m "$MSG"
echo "kilo-shared-save: committed with message: $MSG"
git log -1 --oneline