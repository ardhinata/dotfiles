---
name: project-layout
description: Canonical on-disk directory structure for agentic-driven projects. Use when laying out a new project, diagnosing a missing or wrong path under `.agents/`, `.agents/docs/cache/`, `docs/`, or `.tmp/{notes,plans}/`, when unifying a vendor directory (`.kilo/`, `.claude/`, `.cursor/`, etc.) under `.agents/<vendor>/` with a root symlink, when checking the knowledge-cache layout (date-tag prefix, required README index, one-topic-per-file), or when migrating legacy paths (`.tmp/doc-cache/`, `.help/`, `docs/cache/`). Also load when a project's structure deviates from the canonical tree and the deviation needs justification.
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
.tmp/                              ← transient scratchpad (gitignored)
  notes/                           ← verified, non-obvious task findings
  plans/                           ← in-flight, may survive compaction
```

Ad-hoc subdirectories under `.tmp/` (e.g. `scratch/`, `user_cache/`) are **not canonical**. They appear in some projects but are not sourced by any rule or skill; create them locally if useful, do not promote them to a convention.

## `.tmp/` subroles

Two subdirectories are canonical; both are gitignored by convention. Pick the one that matches the intent.

| Subdir | Intent | When to write | When to delete |
|---|---|---|---|
| `notes/` | Verified, non-obvious, reusable finding captured during a task | Same session the finding is verified; or via deferred capture in the active plan | After promotion to a persistent destination (project-context, knowledge cache, project docs) |
| `plans/` | Multi-step plan that may not survive compaction | Planning a non-trivial task; checkpoint at every milestone | After the task is fully complete and a memory pointer exists |

Filenames in both follow `YYYY-MM-DD-<task-slug>.md` (date-first, ISO 8601) per the `document-conventions` skill, so a flat `ls` is also chronological.

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