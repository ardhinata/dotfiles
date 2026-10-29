---
name: project-layout
description: Use when laying out a new project, diagnosing a missing or wrong path under `.agents/`, `.agents/docs/cache/`, `docs/`, or `.tmp/scratch/`, when unifying a vendor directory (`.cursor/`, `.claude/`, `.opencode/`, etc.) under `.agents/<vendor>/` with a root symlink, when checking the knowledge-cache layout (date-tag prefix, required README index, one-topic-per-file), or when migrating legacy paths (`.tmp/doc-cache/`, `.help/`, `docs/cache/`). Gives the canonical on-disk directory structure for agentic-driven projects. Also load when a project's structure deviates from the canonical tree and the deviation needs justification.
---

# Project Layout

Single source of truth for a **vendor-neutral house layout** for agentic-driven
projects. This skill owns paths and subroles only — the *content* of
`AGENTS.md` lives in the `project-context` skill, the *shape* of each doc type
lives in `document-conventions`.

## Standard vs house style

**Backed by a published standard or convention:**

| Element | Source |
|---|---|
| Root `AGENTS.md` plus nested per-package files, closest wins | agents.md (AAIF, Linux Foundation) |
| `docs/` at the repo root | docs-as-code practice |
| `docs/adr/` | MADR-style ADR collections (MADR itself prescribes `docs/decisions/`) |
| `docs/rfcs/` | Rust RFC, Kubernetes enhancement, IETF RFC 2223 |
| `docs/how-to/` and `docs/reference/` | Diátaxis quadrants |
| `postmortem` spelled as one word | Merriam-Webster headword, Google SRE Book |

**House style.** No external standard covers these — they are this project's
layout, and they should be described as such:

- `.agents/<vendor>/` with a root symlink (the *procedure*. Note that only
  `.agents/skills/` is a discovery location any tool actually scans — see
  "Vendor unification" below)
- `.agents/docs/cache/` with per-topic directories and README indexes
- The `.tmp/{scratch,migration}` role split
- `docs/design/`, `docs/plans/`, and `docs/reference/` as separate trees
- The date-prefixed filename convention
- A split doc as a directory next to its single-file form
  (`docs/plans/<slug>.md` and `docs/plans/<slug>/` are the same doc)

Note that `docs/how-to/` + `docs/reference/` are two of Diátaxis's four
quadrants. Tutorials and explanation are not represented here, so do not
describe this tree as "Diátaxis".

**Harness config directory.** Paths written `~/.config/<vendor>/…` below mean the
harness's user-level config directory: `~/.config/opencode/` in OpenCode.
Skills live in the shared home `~/.agents/skills/`, which most harnesses read.
Claude Code is the exception.

## Canonical layout

```text
AGENTS.md                          ← required pointer target (see project-context)
README.md                          ← required pointer target (see project-context)
docs/                              ← human-facing, hand-written (Standard Readme / Diátaxis)
  plans/                           ← dated plans for work that was executed (committed)
.agents/                           ← unified agent root
  skills/                          ← agent skills, shared by every harness
    <name>/SKILL.md                ← cross-client discovery path: OpenCode, Codex, Cursor,
                                      Gemini CLI, Zed, goose, Amp, Warp, GitHub Copilot
  rules/                           ← shared rule files (house convention — not a discovery
                                     location; each harness loads them through its own
                                     instructions glob)
  agents/                          ← house convention for subagent definitions
  docs/                            ← agent-only docs (fetched references, canonical notes)
    cache/                         ← knowledge cache (date-tagged, tracked, curated)
      README.md                    ← required index
      <topic>/
        README.md
        YYYY-MM-DD-<slug>.md
  <vendor>/                        ← harness-specific assets (rules, commands, hooks)
.tmp/                              ← project-local scratch area (parent dir gitignored)
  scratch/                         ← per-worktree ephemeral (compaction buffers, in-flight tool
                                    output, cursor dumps) — never commit
  migration/                       ← one-time scratch (e.g. chezmoi migration); still gitignored
```

The single sentence that captures the split: `.tmp/scratch/` is
**per-worktree + ephemeral** (gitignored, never committed), `.tmp/migration/`
is **per-project + one-time** (chezmoi or other bootstrap remnants).
Anything that must outlive the worktree belongs in the project repo
(`docs/`) or the knowledge cache (`.agents/docs/cache/`).

## `.tmp/` subroles

Two subdirectories are first-class. Each has a distinct lifetime and commit policy.
Pick the one that matches the intent.

| Subdir | Lifetime | Commit? | When to write | When to delete |
|---|---|---|---|---|
| `scratch/` | Per-working-tree | **Forbidden** | Compaction buffers, in-flight tool output, cursor dumps, anything that must not leak | Whenever the worktree ends (auto via gitignore) |
| `migration/` | Per-project | Forbidden | One-time bootstrap remnants (chezmoi migrations, etc.) | After the migration is complete and verified |

`.tmp/` itself is gitignored at the project root.

## Vendor unification

Two different jobs, two different mechanisms. Do not confuse them.

**Shared skills** go in `.agents/skills/`. It is a cross-client convention,
not a requirement of the skill specification. It is also the only `.agents/`
subdirectory that a shipped tool scans for skills. OpenCode, Codex, Cursor,
Gemini CLI, Zed, goose, Amp, Warp and GitHub Copilot read it at both the
project level and the user level. Factory Droid treats it as a compatibility
path, and its native personal path is `~/.factory/skills/`. GitHub Copilot
reads it in the CLI, the app and the cloud agent, but not in the VS Code
harness. Claude Code is the exception: it reads nothing under `.agents/`, so
it needs `.claude/skills/` with one symlink per skill folder.

**Harness-specific assets** — rule files, custom commands, hooks, MCP
fragments — go in `.agents/<vendor>/` and are reached through the harness's
own root directory. When the project root has a vendor directory
(`.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`,
`.windsurf/`, `.continue/`, and others):

1. Move the directory's contents to `.agents/<vendor>/`.
2. Create a root symlink `<vendor>/` → `.agents/<vendor>/` so vendor tools keep finding their config.
3. Add the symlink pattern to `.gitignore` so the symlink is not committed.
4. Add a `✅ Always` rule to `AGENTS.md` → Boundaries: *recreate the symlink if it is missing on a fresh clone* (`ln -s .agents/<vendor> <vendor>`).

**Know what the vendor subdirectory does and does not buy you.** No tool
scans `.agents/<vendor>/` for discovery. The root symlink is not a
cross-harness bridge — it is how *one* harness reaches *its own* files. The
cross-harness bridge is `.agents/skills/`.

## Knowledge cache

The cache lives at `.agents/docs/cache/` (sibling of `.agents/docs/` for non-cache agent-only docs). Each entry is one topic per file, date-tagged with an ISO 8601 prefix:

```text
.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md
```

A `README.md` index is **required** at `.agents/docs/cache/README.md` (and recommended per topic), with relative links listing every entry (topic, source, capture date, freshness note). Cache entries are tracked in git so a fresh clone inherits them. The cache is never deployed — the repo-root `.agents/` tree does not reach `$HOME`. See `references/knowledge-cache.md` in the `project-context` skill for authoring rules (date tag, source, freshness note).

## Generated content

Generated content has one home per kind. Ask one question: does this need to
be read later, by a human or by a future session?

| Content | Home | Commit? |
|---|---|---|
| A decision, or a plan that was executed | `docs/adr/`, `docs/plans/` | Committed, dated, reviewable |
| A procedure the agent should reuse | `.agents/skills/<name>/SKILL.md` | Committed, agentskills.io format |
| A web-learned fact worth recalling | `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` | Tracked, curated |
| Work still in flight | `.tmp/scratch/` | Gitignored, dies with the worktree |

`.agents/` holds machine-consumed context. `docs/` holds human-reviewed
records. `.tmp/` holds disposable work.

Keep a generated plan in `.tmp/scratch/` only while it is still being written.
Move it to `docs/plans/<YYYY-MM-DD>-<slug>.md` before the work starts, and
keep the filename so the move is a rename. A plan that never moves leaves no
record of what was decided.

## Legacy paths & migration

Older projects may use a non-canonical location for the knowledge cache. Acceptable fallbacks, in order of preference:

| Legacy path | When to migrate |
|---|---|
| `.tmp/doc-cache/` | Project predates `.agents/`; migrate to `.agents/docs/cache/` when convenient |
| `.help/` | Project predates both `.agents/` and the cache convention; migrate when convenient |
| `docs/cache/` | Project prefers a discoverable cache under `docs/`; acceptable as a permanent deviation |

All three are date-tagged under the same `YYYY-MM-DD-<slug>.md` pattern. Only the parent path differs.

## When to deviate

The canonical tree is a default, not a rule. Acceptable deviations include:

- **Existing project** — do not retrofit a tree into a repo that already has a working layout. Document the deviation in the project's `AGENTS.md` → Pointers and move on.
- **Monorepo** — each package may carry its own `AGENTS.md` (closest-to-file wins) but the top-level `.agents/` is shared.
- **Polyglot tooling** — extra vendor directories are fine if they have their own root symlink back to `.agents/<vendor>/`.

When the deviation is structural (a path that contradicts the tree), surface it to the user. Use the harness's question tool, or plain text. Do not silently leave the layout half-canonical.

## References

- `~/.agents/skills/project-context/SKILL.md` — AGENTS.md lifecycle, README↔AGENTS separation, vendoring trigger.
- `~/.agents/skills/document-conventions/SKILL.md` — per-doc-type filename, frontmatter, section order.
- `~/.agents/skills/project-context/references/knowledge-cache.md` — knowledge-cache authoring rules (date tag, source, freshness note).
- `~/.agents/skills/project-context/assets/templates/agents.md` — AGENTS.md template.
- `~/.agents/rules/project-context.md` — router rule that loads this skill on the trigger surface (cache check, missing `AGENTS.md`, vendor dir at root).
- `.agents/docs/cache/README.md` — required cache index (per topic as well).
- `~/.agents/skills/asd-ste100/SKILL.md` — prose-clarity pass (active voice, one idea per sentence, plain words). Load when this skill produces or revises long orientation prose (this `SKILL.md` body, the canonical-layout writeups, the deviation-justification summaries). Apply it after the structural changes settle, before the doc is committed.