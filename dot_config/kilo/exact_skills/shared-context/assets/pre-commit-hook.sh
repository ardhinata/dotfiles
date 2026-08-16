#!/bin/sh
# Pre-commit hook for the per-project shared context repo (.tmp/docs/).
#
# Installed by .kilo/setup-script into each new clone's .git/hooks/pre-commit.
# Checks (in order):
#   1. Reject empty commits.
#   2. Reject any commit containing paths under scratch/.
#   3. Validate date-first filename format for files in notes/, plans/, postmortems/.
#
# The hook does NOT auto-format, lint, or scan for secrets. Keep it fast and
# deterministic.

set -e

# 1. Empty-commit rejection is automatic (git refuses empty commits by default
#    unless --allow-empty is passed). The hook can still abort early if a
#    non-zero staged diff sneaks through via --allow-empty.
if git diff --cached --quiet; then
  echo "pre-commit: refusing empty commit." >&2
  exit 1
fi

# 2. scratch/ path block: any path matching scratch/ in the staged diff is a
#    hard rejection. scratch/ is per-worktree ephemeral and must never enter
#    the shared context repo.
SCRATCH_FILES=$(git diff --cached --name-only | grep -E '(^|/)scratch(/|$)' || true)
if [ -n "$SCRATCH_FILES" ]; then
  echo "pre-commit: refusing to commit scratch/ paths (per-worktree ephemeral)." >&2
  echo "  Staged scratch/ paths:" >&2
  echo "$SCRATCH_FILES" | sed 's/^/    /' >&2
  exit 1
fi

# 3. Date-first filename validation for notes/, plans/, postmortems/.
DATE_REGEX='^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]*\.md$'
INVALID=0
for f in $(git diff --cached --name-only); do
  case "$f" in
    notes/*|plans/*|postmortems/*)
      base=$(basename "$f")
      if ! printf '%s' "$base" | grep -qE "$DATE_REGEX"; then
        echo "pre-commit: invalid filename in $f — must match YYYY-MM-DD-<slug>.md" >&2
        INVALID=1
      fi
      ;;
  esac
done

if [ "$INVALID" = "1" ]; then
  echo "pre-commit: refusing commit; fix filenames and re-stage." >&2
  exit 1
fi

exit 0