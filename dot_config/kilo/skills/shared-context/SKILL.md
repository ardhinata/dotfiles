---
name: shared-context
description: Cross-worktree document sharing via the per-project shared context repo at `.tmp/docs/` (working tree of `~/.local/share/kilo/shared-context/<project-slug>.git/`). Load when writing to or reading from `.tmp/docs/{notes,plans,postmortems,user_cache}/`, when the user asks how Agent Manager worktrees share context, when initializing a new project's shared context (first worktree on a project), when reconciling cross-worktree filename collisions, when committing with `kilo-shared-save`, or when recovering an abandoned branch in the shared context repo. Does not own project-tree placement — load the `project-layout` skill for the canonical layout.
---

# Shared Context

A per-project git repository that holds the agent's documents (notes,
plans, postmortems, persistent user scratch). Each Agent Manager
worktree checks out a separate branch in this shared repo, commits
its writes, and pulls changes from siblings. The mechanism makes
`.tmp/docs/` cross-worktree-visible **and** cross-machine-visible per
the local bare repo's lifetime.

This skill is the canonical reference for the mechanism. The
project-layout skill defines the path conventions; this skill defines
the protocol.

## When to load

- Writing or reading from `.tmp/docs/{notes,plans,postmortems,user_cache}/`
- Initializing a new project's shared context on first worktree spawn
- Reconciling cross-worktree filename collisions (`YYYY-MM-DD-<slug>.md`
  produced in two worktrees diverge in git)
- Committing with `kilo-shared-save`
- Recovering a branch from a destroyed worktree
- The user asks "why isn't my note showing up in the other worktree?"
- Editing `.kilo/setup-script` to install the hook + clone wrapper

## How this skill is organised

| File | When to read |
|---|---|
| [`assets/kilo-shared-save.sh`](assets/kilo-shared-save.sh) | The commit wrapper. Source of truth — copy verbatim into the user's `~/.local/share/kilo/bin/`. |
| [`assets/pre-commit-hook.sh`](assets/pre-commit-hook.sh) | The hook installed in every new clone's `.git/hooks/pre-commit/`. Source of truth. |
| [`references/recovery.md`](references/recovery.md) | Recovering an abandoned branch from a destroyed worktree; clean-up of stale branches. |

## Concepts

### Bare repo location

`~/.local/share/kilo/shared-context/<project-slug>.git/`

`<project-slug>` = `<basename>-<short-hash-of-abs-path>`, where
`<basename>` is the basename of the project root (e.g. `chezmoi`,
`notes-`) and `<short-hash-of-abs-path>` is a 6-character hash of the
absolute project path. Two `chezmoi` repos at different paths get
different slugs; the same repo on different machines gets the **same**
slug (the abs-path is stable per checkout).

The bare repo lives **outside** any project tree. It is local-only —
no remote is configured. No cross-machine sync; cross-machine survival
requires either backing up `~/.local/share/` or pushing to a remote
(out of scope for the locked 2026-08-10 design).

### Working tree

`<project>/.tmp/docs/` — a full `git clone` of the bare repo. Each
Agent Manager worktree has its own clone. Clones share the same bare
repo but live in different worktrees (different `.tmp/docs/` paths).

Per worktree, the working tree is on branch `<worktree-slug>` (the
slug Kilo's Agent Manager uses for the project repo, e.g.
`therapeutic-diascia`).

### The four subdirs

| Subdir | Purpose | Commit? |
|---|---|---|
| `notes/` | Date-first findings (per `proactive-note-capture.md`) | Yes |
| `plans/` | Date-first in-flight plans (per `plans.md`) | Yes |
| `postmortems/` | Date-first incident write-ups | Yes |
| `user_cache/` | Per-project user scratch that should persist across worktrees | Yes |

Anything **not** in `.tmp/docs/` (e.g. `.tmp/scratch/`) is **not**
part of the shared context repo. The hook rejects commits that
contain `scratch/` paths.

## Workflow

### On first worktree of a project

The project's `.kilo/setup-script` (or equivalent) detects no bare
repo at `~/.local/share/kilo/shared-context/<slug>.git/` and runs the
init sequence:

```sh
git init --bare "$HOME/.local/share/kilo/shared-context/<slug>.git"
git clone "$HOME/.local/share/kilo/shared-context/<slug>.git" .tmp/docs
cd .tmp/docs
mkdir -p notes plans postmortems user_cache
touch notes/.gitkeep plans/.gitkeep postmortems/.gitkeep user_cache/.gitkeep
git add .
git commit -m "init: shared context scaffold"
git checkout -b <worktree-slug>
cp "$REPO_PATH/.agents/kilo/shared-context-assets/pre-commit-hook.sh" \
   .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The setup script also writes `README.md` into `.tmp/docs/` explaining
the convention.

### On each subsequent worktree

```sh
git clone "$HOME/.local/share/kilo/shared-context/<slug>.git" .tmp/docs
cd .tmp/docs
git checkout -b <worktree-slug>
cp "$REPO_PATH/.agents/kilo/shared-context-assets/pre-commit-hook.sh" \
   .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

If the worktree is being created from a sibling worktree that already
has a clone, the setup script may detect the existing clone and skip
the re-clone (`./tmp/docs/` is gitignored at the project root, so
sibling worktrees start empty).

### On every write to `.tmp/docs/`

```sh
kilo-shared-save "<short-message>"
```

This wrapper:

1. `cd`s to `$KILO_SHARED_CONTEXT_PATH` (set by the setup script in
   the agent's environment).
2. `git add -A`
3. `git commit -m "$1"` (rejects empty commits via the hook)
4. Reports the commit hash.

**Do not** write to `.tmp/docs/` without committing — uncommitted
state vanishes on worktree destroy and is invisible to siblings.

### Pre-create scan (collision check)

Before creating a new note/plan/postmortem:

```sh
kilo-shared-pull origin main   # or: git fetch origin main
```

Then `ls` the target dir for same-`YYYY-MM-DD` slugs. The shared
context repo's branch named `main` accumulates every worktree's
work (via merges); pulling it surfaces cross-worktree collisions
that a local `ls` would miss.

### Cross-worktree reconciliation

If two worktrees produce the same filename:

1. **Prevention:** always pre-create-scan with
   `kilo-shared-pull origin main`. Filename collisions are easy to
   avoid by appending `-<worktree-slug>` or a counter.
2. **Resolution:** the worktree that committed first wins on the
   shared `main` branch. The other worktree, on pull, sees the
   conflict and either:
   - Fast-forwards if there are no local commits on the same path
   - Rejects the merge if both branches modified it; the agent runs
     `git merge --no-ff` and reconciles by hand

The hook does **not** auto-merge. Conflict reconciliation is the
agent's job.

## What the mechanism is NOT

- **Not a remote.** No cross-machine sync.
- **Not a replacement for project memory.** Notes/plans/postmortems
  are agent-side scratch. Project source, AGENTS.md, and tracked
  docs remain canonical.
- **Not shared with Kilo runtime.** `agent-manager.json` is
  Kilo-managed, separate from this repo.
- **Not a backup.** The bare repo dies with `~/.local/share/`. Add
  a remote or back up the bare directory if durability matters.

## Anti-patterns

- **Writing to `.tmp/notes/`/`plans/`/`user_cache/`** instead of
  `.tmp/docs/`. The legacy dirs are not part of the shared context
  repo. Files written there vanish on worktree destroy.
- **Skipping `kilo-shared-save`** after a write. Uncommitted state is
  invisible to siblings.
- **Committing `scratch/` paths.** The hook rejects them; the agent
  must not stage them.
- **Hard-coding `~/.local/share/kilo/shared-context/<slug>` in the
  agent's reasoning.** Use `$KILO_SHARED_CONTEXT_PATH` (env var set by
  the setup script) or the bare-path lookup function the wrapper
  exposes.
- **Reaching into another worktree's `.tmp/docs/` directly.** Always
  go through `git fetch` + `git checkout` (or `kilo-shared-pull`).