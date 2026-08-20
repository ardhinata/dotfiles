#!/bin/sh
# kilo-shared-init — bootstrap script for the per-project shared context repo.
# Called via `kilo-shared init` (subcommand dispatch in kilo-shared.sh).
#
# Checks (all idempotent — safe to re-run):
#   1. Bare repo at ~/.local/share/kilo/shared-context/<slug>.git/ — create if missing.
#   2. Clone at <project>/.tmp/docs/ — create if missing.
#   3. Four subdirs (notes/, plans/, postmortems/, user_cache/) + .gitkeep files.
#   4. Initial scaffold commit on empty repo.
#   5. Per-worktree branch (skip on the main checkout).
#   6. Pre-commit hook at <project>/.tmp/docs/.git/hooks/pre-commit — install
#      from the chezmoi asset; overwrite with --force.
#
# Flags:
#   --here   Use pwd as the project root (skip auto-detection).
#   --force  Overwrite existing dirs / hook without prompting.
#
# Slug rule: <basename>-<6-char-hash-of-abs-path>. Two chezmoi repos at
# different paths get different slugs; the same repo on different machines
# gets the same slug.

set -e

if [ -z "$KILO_SHARED_INIT_PROJECT_ROOT" ]; then
  echo "kilo-shared-init: KILO_SHARED_INIT_PROJECT_ROOT must be set by the caller." >&2
  echo "  (kilo-shared init handles this; do not run this script directly.)" >&2
  exit 2
fi

PROJECT_ROOT="$KILO_SHARED_INIT_PROJECT_ROOT"
FORCE="${KILO_SHARED_INIT_FORCE:-0}"

PROJ_BASENAME=$(basename "$PROJECT_ROOT")
PROJ_HASH=$(printf '%s' "$PROJECT_ROOT" | sha256sum | head -c 6)
PROJ_SLUG="${PROJ_BASENAME}-${PROJ_HASH}"
BARE_REPO="$HOME/.local/share/kilo/shared-context/${PROJ_SLUG}.git"
DOCS_PATH="$PROJECT_ROOT/.tmp/docs"

# 1. Bare repo
if [ -d "$BARE_REPO" ]; then
  echo "init: bare repo exists at $BARE_REPO"
else
  mkdir -p "$(dirname "$BARE_REPO")"
  git init --bare "$BARE_REPO" --initial-branch=main >/dev/null
  git -C "$BARE_REPO" symbolic-ref HEAD refs/heads/main
  echo "init: created bare repo at $BARE_REPO"
fi

# 2. Clone
if [ -d "$DOCS_PATH/.git" ]; then
  echo "init: working tree exists at $DOCS_PATH"
else
  if [ -d "$DOCS_PATH" ] && [ -n "$(ls -A "$DOCS_PATH" 2>/dev/null)" ]; then
    echo "init: $DOCS_PATH exists but is not a git working tree; aborting." >&2
    echo "      Remove the dir or pass --force to override after manual cleanup." >&2
    if [ "$FORCE" -ne 1 ]; then
      exit 1
    fi
    rm -rf "$DOCS_PATH"
  fi
  mkdir -p "$(dirname "$DOCS_PATH")"
  git clone "$BARE_REPO" "$DOCS_PATH" >/dev/null
  echo "init: cloned bare repo to $DOCS_PATH"
fi

# 3. Subdirs + .gitkeep
cd "$DOCS_PATH"
for d in notes plans postmortems user_cache; do
  mkdir -p "$d"
  touch "$d/.gitkeep"
done

# 4. Initial scaffold commit on empty repo
if [ -z "$(git rev-list --all --count 2>/dev/null)" ] || [ "$(git rev-list --all --count)" = "0" ]; then
  git add -A
  git -c user.email='kilo-shared@local' -c user.name='kilo-shared init' \
    commit -m "init: shared context scaffold" >/dev/null
  echo "init: scaffold commit created"
fi

# 5. Per-worktree branch
WORKTREE_SLUG=$(basename "$PROJECT_ROOT")
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [ "$CURRENT_BRANCH" = "main" ] && [ "$WORKTREE_SLUG" != "$PROJ_BASENAME" ]; then
  git checkout -b "$WORKTREE_SLUG" >/dev/null
  echo "init: created worktree branch: $WORKTREE_SLUG"
fi

# 6. Pre-commit hook
mkdir -p .git/hooks
HOOK_ASSET="$HOME/.local/share/chezmoi/dot_config/kilo/exact_skills/shared-context/assets/pre-commit-hook.sh"
if [ ! -f "$HOOK_ASSET" ]; then
  HOOK_ASSET="$PROJECT_ROOT/.agents/kilo/shared-context-assets/pre-commit-hook.sh"
fi
if [ -f "$HOOK_ASSET" ]; then
  if [ -f .git/hooks/pre-commit ] && [ "$FORCE" -ne 1 ]; then
    echo "init: pre-commit hook already installed (pass --force to overwrite)"
  else
    cp "$HOOK_ASSET" .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "init: installed pre-commit hook from $HOOK_ASSET"
  fi
else
  echo "init: WARNING pre-commit-hook.sh asset not found; hook not installed." >&2
fi

echo "init: done."
