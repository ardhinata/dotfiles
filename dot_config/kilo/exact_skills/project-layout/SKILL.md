---
name: project-layout
description: Canonical on-disk directory structure for agentic-driven projects. Use when laying out a new project, diagnosing a missing or wrong path under `.agents/`, `.agents/docs/cache/`, `docs/`, or `.tmp/{docs,scratch}/`, when unifying a vendor directory (`.kilo/`, `.claude/`, `.cursor/`, etc.) under `.agents/<vendor>/` with a root symlink, when checking the knowledge-cache layout (date-tag prefix, required README index, one-topic-per-file), when explaining the shared-context repo at `.tmp/docs/` (per-worktree clone of `~/.local/share/kilo/shared-context/<project>.git/`), or when migrating legacy paths (`.tmp/doc-cache/`, `.help/`, `docs/cache/`). Also load when a project's structure deviates from the canonical tree and the deviation needs justification.
---

# Project Layout

Single source of truth for the **standard on-disk tree** every agentic-driven project should converge on. This skill owns paths and subroles only — the *content* of `AGENTS.md` lives in the `project-context` skill, the *shape* of each doc type lives in `document-conventions`.

## Canonical layout

```text
AGENTS.md                          ← required pointer target (see project-context)
README.md                          ← required pointer target (see project-context)
docs/                              ← human-facing, hand-written (Standard Readme / Diátaxis)
.agents/                           ← unified agent-only root
  <vendor>/                        ← .kilo/, .claude/, .cursor/, etc. live here
  docs/                            ← agent-only docs (fetched references, canonical notes)
    cache/                         ← knowledge cache (date-tagged, gitignored)
      README.md                    ← required index
      <topic>/
        README.md
        YYYY-MM-DD-<slug>.md
.tmp/                              ← project-local scratch area (parent dir gitignored)
  docs/                            ← working tree of shared-context repo (per-worktree clone)
    notes/                         ← date-first findings (committed via kilo-shared save)
    plans/                         ← date-first in-flight plans (committed)
    postmortems/                   ← date-first incident write-ups (committed)
    user_cache/                    ← ad-hoc user scratch that should persist (committed)
    README.md                      ← explains the shared-context convention
  scratch/                         ← per-worktree ephemeral (compaction buffers, in-flight tool
                                     output, cursor dumps) — never commit
  migration/                       ← one-time scratch (e.g. chezmoi migration); still gitignored
```

The single sentence that captures the split: `.tmp/docs/` is **shared + persistent**
(versioned in a per-machine bare git repo, branch per worktree), `.tmp/scratch/`
is **per-worktree + ephemeral** (gitignored, never committed), `.tmp/migration/`
is **per-project + one-time** (chezmoi or other bootstrap remnants).

## `.tmp/` subroles

Three subdirectories are first-class; each has a distinct lifetime and commit policy.
Pick the one that matches the intent.

| Subdir | Lifetime | Commit? | When to write | When to delete |
|---|---|---|---|---|
| `docs/` | Across worktrees + machines (git-tracked) | **Required** — `kilo-shared save` after each write | Verified findings, in-flight plans, postmortems, persistent user scratch | Never directly; only `git rm` if a doc is actively retracted |
| `scratch/` | Per-working-tree | **Forbidden** | Compaction buffers, in-flight tool output, cursor dumps, anything that must not leak | Whenever the worktree ends (auto via gitignore) |
| `migration/` | Per-project | Forbidden | One-time bootstrap remnants (chezmoi migrations, etc.) | After the migration is complete and verified |

`.tmp/` itself is gitignored at the project root (the bare repo for `.tmp/docs/`
lives outside the project at `~/.local/share/kilo/shared-context/<project-slug>.git/`).
See "Shared context repo" below for the full mechanics.

Filenames in `.tmp/docs/{notes,plans,postmortems}/` follow `YYYY-MM-DD-<task-slug>.md`
(date-first, ISO 8601) per the `document-conventions` skill, so a flat `ls` is also
chronological. **Filename uniqueness across worktrees is now load-bearing** — the
same `YYYY-MM-DD-<slug>.md` produced in two worktrees will diverge in git and require
manual reconciliation. Pre-create scan in `document-conventions` enforces local
uniqueness; the shared-context mechanism requires `git fetch origin main` before
creating a new note to detect cross-worktree collisions.

## Shared context repo

The mechanism that makes `.tmp/docs/` cross-worktree and cross-machine is a separate
bare git repo, **per project**, living outside any project tree at
`~/.local/share/kilo/shared-context/<project-slug>.git/`. Project slug is
`<basename>-<short-hash-of-abs-path>` (e.g. `chezmoi-7a3b9c`) to avoid collisions
between two repos with the same basename.

### Mechanics

1. **First worktree on a given project** (setup script runs `kilo-setup-shared-context`):
   - `git init --bare ~/.local/share/kilo/shared-context/<slug>.git`
   - `git clone ~/.local/share/kilo/shared-context/<slug>.git .tmp/docs`
   - Populate `.tmp/docs/{notes,plans,postmortems,user_cache}/` with `.gitkeep`
   - Initial commit with `README.md` explaining the convention + commit protocol
   - Create `pre-commit` hook (filename format + scratch-block + empty rejection)
2. **Each subsequent worktree** (same setup script):
   - `git clone ~/.local/share/kilo/shared-context/<slug>.git .tmp/docs`
     (or `git fetch` + `git checkout` if a clone already exists from a sibling
     worktree — setup script detects and unifies)
   - `git checkout -b <worktree-slug>` (branch name = the worktree slug Kilo
     already uses for the project repo, e.g. `therapeutic-diascia`)
   - Install the same `pre-commit` hook
3. **Every write to `.tmp/docs/{notes,plans,postmortems,user_cache}/`** must end with
   `kilo-shared save "<short-message>"`, a wrapper installed at
   `~/.local/share/kilo/bin/kilo-shared` by the setup script. The wrapper
   runs `git add -A && git commit -m "$1"` from `$KILO_SHARED_CONTEXT_PATH`
   (set by the setup script, exported into the agent's environment).
4. **On worktree destroy**, the branch in the shared context repo is **kept forever**
   (per the locked design decision). Manual cleanup:
   `git -C ~/.local/share/kilo/shared-context/<slug>.git/ branch -d <worktree-slug>`.

### What the shared context repo is NOT

- **Not a remote.** Bare repos live per-machine. No cross-machine sync. (Adding
  a remote is a future option; not in scope for the locked design.)
- **Not a replacement for project memory.** Notes and plans are agent-side
  scratch; the project repo's source code, AGENTS.md, and tracked docs remain
  the canonical project state.
- **Not shared with Kilo runtime.** `agent-manager.json` is still Kilo-managed
  and not in this repo.

### Conflict policy

Two worktrees writing the same `YYYY-MM-DD-<slug>.md` produce a branch divergence
in the shared context repo. Resolution:

1. **Pre-create scan.** Before writing, `git fetch origin main && git log origin/main -- <dir>/<slug>*`
   to detect collisions before they happen.
2. **If a collision exists**, either pick a different slug
   (`<YYYY-MM-DD>-<slug>-<worktree-tag>`) or `git merge origin/<worktree-slug>`
   manually. The pre-commit hook does NOT auto-merge; it rejects empty commits
   and rejects `scratch/` commits, but does not arbitrate content conflicts.
3. **At merge time** (when the project worktree branch merges back to main and
   another wants to pull it in), the agent runs
   `kilo-shared pull origin main` which fast-forwards or surfaces the
   conflict.

See the `shared-context` skill for the canonical reference and the bundled
`assets/{pre-commit-hook.sh,kilo-shared.sh,kilo-helper-shared-detect.sh,kilo-shared-init.sh}` starters.

## Vendor unification

When the project root contains a vendor-specific directory (`.kilo/`, `.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`, `.windsurf/`, `.continue/`, etc.), consolidate under `.agents/<vendor>/`:

1. Move the directory's contents to `.agents/<vendor>/`.
2. Create a root symlink `<vendor>/` → `.agents/<vendor>/` so vendor tools keep finding their config.
3. Add the symlink pattern to `.gitignore` so the symlink is not committed.
4. Add a `✅ Always` rule to `AGENTS.md` → Boundaries: *recreate the symlink if it is missing on a fresh clone* (`ln -s .agents/<vendor> <vendor>`).

The phase-3 *trigger* (a vendor directory at the project root) lives in the `project-context` skill; this skill owns only the **mechanics** above.

## Knowledge cache

The cache lives at `.agents/docs/cache/` (sibling of `.agents/docs/` for non-cache agent-only docs). Each entry is one topic per file, date-tagged with an ISO 8601 prefix:

```text
.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md
```

A `README.md` index is **required** at `.agents/docs/cache/README.md` (and recommended per topic), with relative links listing every entry (topic, source, capture date, freshness note). Cache entries are gitignored — they are scratch space, not documentation. See `references/knowledge-cache.md` in the `project-context` skill for authoring rules (date tag, source, freshness note).

## Legacy paths & migration

Older projects may use a non-canonical location for the knowledge cache. Acceptable fallbacks, in order of preference:

| Legacy path | When to migrate |
|---|---|
| `.tmp/doc-cache/` | Project predates `.agents/`; migrate to `.agents/docs/cache/` when convenient |
| `.help/` | Project predates both `.agents/` and the cache convention; migrate when convenient |
| `docs/cache/` | Project prefers a discoverable cache under `docs/`; acceptable as a permanent deviation |

All three are date-tagged under the same `YYYY-MM-DD-<slug>.md` pattern; only the parent path differs.

## When to deviate

The canonical tree is a default, not a rule. Acceptable deviations include:

- **Existing project** — do not retrofit a tree into a repo that already has a working layout. Document the deviation in the project's `AGENTS.md` → Pointers and move on.
- **Monorepo** — each package may carry its own `AGENTS.md` (closest-to-file wins) but the top-level `.agents/` is shared.
- **Polyglot tooling** — extra vendor directories are fine if they have their own root symlink back to `.agents/<vendor>/`.

When the deviation is structural (a path that contradicts the tree), surface it to the user via the `question` tool — do not silently leave the layout half-canonical.

## References

- `~/.config/kilo/skills/project-context/SKILL.md` — AGENTS.md lifecycle, README↔AGENTS separation, vendoring trigger.
- `~/.config/kilo/skills/document-conventions/SKILL.md` — per-doc-type filename, frontmatter, section order.
- `~/.config/kilo/skills/project-context/references/knowledge-cache.md` — knowledge-cache authoring rules (date tag, source, freshness note).
- `~/.config/kilo/skills/project-context/assets/templates/agents.md` — AGENTS.md template.
- `~/.config/kilo/rules/project-context.md` — router rule that loads this skill on the trigger surface (cache check, missing `AGENTS.md`, vendor dir at root).
- `.agents/docs/cache/README.md` — required cache index (per topic as well).
- `~/.config/kilo/skills/asd-ste100/SKILL.md` — prose-clarity pass (active voice, one idea per sentence, plain words). Load when this skill produces or revises long orientation prose (this `SKILL.md` body, the canonical-layout writeups, the deviation-justification summaries). Apply it after the structural changes settle, before the doc is committed.