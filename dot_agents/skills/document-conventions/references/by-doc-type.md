# Per-Doc-Type Conventions

The full reference for each doc type the agent creates or edits. Use this
table to confirm filename, frontmatter, sections, ordering, and length
after you have picked a type from the
[decision matrix](decision-matrix.md).

## How to read this table

Each row covers one doc type. Columns:

- **Filename pattern** — exact glob; `<…>` are placeholders.
- **Frontmatter** — required / optional / forbidden; field schema if
  present.
- **Required sections** — minimum set the type *must* include.
- **Optional sections** — common additions that may appear.
- **Section order** — fixed / loose / none.
- **Length budget** — target and hard ceiling, in lines.
- **Validation** — how to verify it follows the convention.
- **Source** — where the rule comes from.

## Table of contents

1. [Rule file](#rule-file)
2. [SKILL.md (skill)](#skillmd)
3. [Skill reference file](#skill-reference-file)
4. [AGENTS.md](#agentsmd)
5. [README.md](#readmemd)
6. [Topic README.md](#topic-readmemd)
7. [Knowledge-cache entry](#knowledge-cache-entry)
8. [Knowledge-cache topic README.md](#knowledge-cache-topic-readmemd)
9. [Knowledge-cache root README.md](#knowledge-cache-root-readmemd)
10. [Postmortem (docs/post-mortem/)](#postmortem)
11. [Persistent plan](#persistent-plan)
12. [Transient plan](#transient-plan)
13. [ADR (MADR)](#adr-madr)
14. [RFC](#rfc)
15. [Design doc](#design-doc)
16. [CHANGELOG.md](#changelogmd)
17. [CONTRIBUTING.md](#contributingmd)
18. [.tmp/scratch](#tmpscratch)
19. [.tmp/migration](#tmpmigration)
20. [Tutorial / how-to / reference / explanation (Diátaxis)](#diataxis-quadrants)

---

## Rule file

| Field | Value |
|---|---|
| Path | `~/.agents/rules/<slug>.md` |
| Frontmatter | **Forbidden.** Project decision. Frontmatter is a Cursor `.mdc` convention that no rule loader parses. |
| Required sections | One-line description (no heading), `## When` (or similar trigger header), the rule body |
| Optional sections | `## When to load`, `## Captured …`, `## Anti-patterns`, `## References` |
| Section order | Loose |
| Length budget | Target 30–80 lines, hard ceiling 150 |
| Validation | Manual review against `rules.personal.d/` style. No frontmatter parser exists. |
| Source | Global decision; see `~/.agents/rules/*.md` for examples |

**Slug rules:** lowercase, hyphens, no trailing punctuation. Match the
intent, not the filename (e.g. `fnm.md` not `node-version-management.md`).

---

## SKILL.md

| Field | Value |
|---|---|
| Path | `~/.agents/skills/<slug>/SKILL.md` (or project-local `.agents/skills/<slug>/`, `.<vendor>/skills/<slug>/`) |
| Frontmatter | **Required.** `name` (≤ 64 chars, lowercase letters/digits/hyphens, no `--`, no leading/trailing hyphen, matches parent dir), `description` (≤ 1024 chars, non-empty, third person, names *what* and *when*). Optional: `license`, `compatibility` (≤ 500 chars), `metadata`, `allowed-tools` (experimental). |
| Required sections | H1 (the skill's name or one-line summary), body content per the agentskills.io "Recommended sections" — step-by-step instructions, examples, edge cases |
| Optional sections | `## When to load`, `## Quick start`, `## Workflow`, `## Anti-patterns`, `## References`, `## Captured …` |
| Section order | Loose but progressive: orient → quick start → details → edge cases → anti-patterns → references |
| Length budget | Target < 300 lines; hard ceiling 500 lines. Beyond this, split into `references/*.md` |
| Validation | `skills-ref validate ./<skill-dir>` (if `skills-ref` on PATH). Manual review: frontmatter fields present, name matches dir, description in third person with key terms |
| Source | [agentskills.io specification](https://agentskills.io/specification); [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices); [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills); the project's `agent-context` skill (`.agents/skills/agent-context/SKILL.md`, project-local — not installed globally). |

---

## Skill reference file

| Field | Value |
|---|---|
| Path | `~/.agents/skills/<slug>/references/<file>.md` |
| Frontmatter | None |
| Required sections | H1 (matching filename slug), body |
| Optional sections | TOC if file > 100 lines, link back to `SKILL.md` |
| Section order | Loose |
| Length budget | As needed; 100+ line files require TOC |
| Validation | Linked from `SKILL.md`; one level deep from `SKILL.md` (avoid reference chains) |
| Source | agentskills.io — "Keep file references one level deep from SKILL.md" |

---

## AGENTS.md

| Field | Value |
|---|---|
| Path | `AGENTS.md` at the repo root, and one nested per monorepo package |
| Frontmatter | **Forbidden.** Plain Markdown only. |
| Required sections | At minimum, a `Pointers` section referencing `README.md` and any skill/rule folders. Strong recommendation: `Boundaries` (`✅ Always` / `⚠️ Ask first` / `🚫 Never`). |
| Optional sections | `Purpose`, `Stack`, `Commands`, `Code style`, `Testing rules`, `Boundaries`, `Pointers` |
| Section order | Loose — the agents.md spec is free-form |
| Length budget | Target 40–80 lines, hard ceiling 150 (global rule) |
| Validation | Manual review; nested AGENTS.md overrides root when closer to edited file; closest-wins |
| Source | [agents.md](https://agents.md/); [project-context skill](../../project-context/SKILL.md); Gloaguen et al., arXiv:2602.11988 (cost of LLM-generated context files) |

**Key rule:** every line must answer "would an agent get this wrong
without it?". Cut otherwise.

---

## README.md

| Field | Value |
|---|---|
| Path | `README.md` at repo root; `README.<lang>.md` for translations (BCP 47) |
| Frontmatter | None |
| Required sections | Title (H1), Short Description (< 120 chars, no `>`, own line, on its own line), Install, Usage, Contributing, License — per Standard Readme. English README must be `README.md`. |
| Optional sections | Banner, Badges, Long Description, ToC, Security, Background, API, Maintainers, Thanks |
| Section order | **Fixed** by Standard Readme: Title → Banner → Badges → Short Description → Long Description → ToC → Security → Background → Install → Usage → Extra → API → Maintainers → Thanks → Contributing → License |
| Length budget | Target < 200 lines; "comprehensive" 200–500. Move longer material to `docs/` |
| Validation | Standard Readme linter (`standard-readme-preset`); or manual checklist in [`assets/checklists.md`](../assets/checklists.md) |
| Source | [Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md); [Make a README](https://www.makeareadme.com/); [GitHub Docs — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) |

---

## Topic README.md

| Field | Value |
|---|---|
| Path | `<dir>/README.md` (e.g. `docs/README.md`, `.agents/<vendor>/skills/README.md`) |
| Frontmatter | None |
| Required sections | Title, brief intro paragraph, table of contents or index of children |
| Optional sections | "How to use this folder", "Adding to this folder" |
| Section order | Loose |
| Length budget | < 80 lines |
| Validation | Manual — children should link to the topic README and vice versa |
| Source | GitHub convention; project-context skill |

---

## Knowledge-cache entry

| Field | Value |
|---|---|
| Path | `.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md` |
| Frontmatter | Optional. Common fields: `source`, `captured`, `freshness`, `tags` |
| Required sections | H1 (topic or finding), body |
| Optional sections | `## Source`, `## Captured`, `## Freshness note`, `## Unverified`, `## See also` |
| Section order | Loose |
| Length budget | 30–150 lines |
| Validation | Linked from the topic `README.md` (and root `README.md` if topic is new). Filename must match ISO date prefix and a lowercase-hyphen slug |
| Source | Global rules: `project-context.md`, `web-verification.md` |

---

## Knowledge-cache topic README.md

| Field | Value |
|---|---|
| Path | `.agents/docs/cache/<topic>/README.md` |
| Frontmatter | None |
| Required sections | H1 (topic), short description, "Entries" table linking every entry by relative path with date and source |
| Optional sections | "How this topic is curated", "Related topics" |
| Section order | Loose; entries list near top |
| Length budget | < 100 lines |
| Validation | Every entry file in this directory appears in the table |
| Source | `~/.agents/skills/project-context/references/knowledge-cache.md`; `web-verification.md` (global rule) |

---

## Knowledge-cache root README.md

| Field | Value |
|---|---|
| Path | `.agents/docs/cache/README.md` |
| Frontmatter | None |
| Required sections | H1 ("Knowledge cache"), intro, "Topics" table linking every topic directory's `README.md` |
| Optional sections | "Cache policy", "How to add a topic" |
| Section order | Loose; topics list near top |
| Length budget | < 100 lines |
| Validation | Every topic directory appears in the table |
| Source | `project-context.md`; `web-verification.md` |

---

## Postmortem

| Field | Value |
|---|---|
| Path | `docs/post-mortem/<YYYY-MM-DD>-<slug>.md`, or `docs/post-mortem/<YYYY-MM-DD>-<slug>/` with `README.md` + `NN-<section>.md` when split |
| Lifetime | Git-tracked in the project repo. |
| Commit policy | Committed with the project repo. |
| Frontmatter | Optional. Recommended: `severity`, `status`, `date` |
| Required sections | H1, `## Summary`, `## Timeline`, `## Root cause`, `## Impact`, `## Action items` |
| Optional sections | `## Detection`, `## Resolution`, `## Lessons learned`, `## See also` |
| Section order | Loose; the above is conventional |
| Length budget | 50–300 lines |
| Validation | Linked from any active runbook or related doc; action items moved into a durable tracker |
| Source | `document-conventions` skill (post-mortem tree under `docs/`) |

---

## Persistent plan

| Field | Value |
|---|---|
| Path | `docs/plans/<YYYY-MM-DD>-<task-slug>.md` (user-specified paths allowed), or `docs/plans/<YYYY-MM-DD>-<task-slug>/` with `README.md` + `NN-<section>.md` when split |
| Frontmatter | Optional. Recommended: `status` (`draft`/`active`/`completed`/`abandoned`), `owner`, `last-updated` |
| Required sections | H1, `## Goal`, `## Scope`, `## Steps`, `## Status` |
| Optional sections | `## Decisions`, `## Risks`, `## Open questions`, `## Related` |
| Section order | Loose |
| Length budget | < 500 lines; over the ceiling, split into a directory (see [structure-and-length.md](structure-and-length.md#when-a-doc-outgrows-its-file)) or link out to design docs / ADRs |
| Validation | User-approved path; same fields as the [transient plan](#transient-plan) but durable |
| Source | `document-conventions` skill; per-user quirks live at `~/.agents/rules.personal.d/*.md` |

---

## Transient plan

| Field | Value |
|---|---|
| Path | `.tmp/scratch/<YYYY-MM-DD>-<task-slug>.md` |
| Lifetime | Per-working-tree. Gitignored. |
| Commit policy | **Forbidden.** Never stage this path. |
| Frontmatter | None |
| Required sections | None |
| Optional sections | Any of the [persistent plan](#persistent-plan) sections |
| Section order | None |
| Length budget | None |
| Validation | `.tmp/` is gitignored. Promote to `docs/plans/<YYYY-MM-DD>-<task-slug>.md` before the work starts, keeping the filename |
| Source | `project-layout` skill (`.tmp/` subroles); `decision-matrix.md` |

---

## ADR (MADR)

| Field | Value |
|---|---|
| Path | `docs/adr/NNNN-<slug>.md` (NNNN = 4-digit zero-padded sequence) |
| Frontmatter | Optional. Recommended: `status` (`proposed`/`rejected`/`accepted`/`deprecated`/`superseded by ADR-NNNN`), `date`, `decision-makers`, `consulted`, `informed` |
| Required sections | Title, `## Context and Problem Statement`, `## Considered Options`, `## Decision Outcome` |
| Optional sections | `## Decision Drivers`, `### Consequences` (Good/Bad/Neutral), `### Confirmation`, `## Pros and Cons of the Options` (per option), `## More Information` |
| Section order | **Fixed** per MADR: Title → Context → Drivers → Considered Options → Decision Outcome → Consequences → Confirmation → Pros/Cons → More Info |
| Length budget | 50–200 lines |
| Validation | Numbering without gaps; status field present and accurate; superseded ADRs reference their successor |
| Source | [MADR](https://adr.github.io/madr/); [adr.github.io](https://adr.github.io/); Nygard 2011 "Documenting Architecture Decisions" |

---

## RFC

| Field | Value |
|---|---|
| Path | `docs/rfcs/NNNN-<slug>.md`, or `docs/rfcs/NNNN-<slug>/` with `README.md` + `NN-<section>.md` when split |
| Frontmatter | Optional. Recommended: `status` (`draft`/`review`/`accepted`/`rejected`/`withdrawn`), `reviewers`, `deadline`, `last-updated` |
| Required sections | H1 (slug title), `## Summary`, `## Motivation`, `## Detailed design`, `## Drawbacks`, `## Alternatives`, `## Open questions`, `## Unresolved questions` |
| Optional sections | `## Prior art`, `## Future possibilities`, `## Implementation plan`, `## Acknowledgements` |
| Section order | Loose; common IETF-inspired order above |
| Length budget | 200–1000 lines |
| Validation | Reviewers listed; deadline set; status updated when feedback closes |
| Source | IETF RFC 2119/8174 (key words); common `docs/rfcs/` pattern from Kubernetes, Rust, React |

---

## Design doc

| Field | Value |
|---|---|
| Path | `docs/design/<slug>.md`, or `docs/design/<slug>/` with `README.md` + `NN-<section>.md` when split |
| Frontmatter | Optional. Recommended: `status`, `last-updated` |
| Required sections | H1, `## Problem`, `## Goals / non-goals`, `## Proposed design`, `## Alternatives considered` |
| Optional sections | `## Open questions`, `## Implementation plan`, `## Testing`, `## Risks` |
| Section order | Loose |
| Length budget | 500–2000 lines |
| Validation | Goals/non-goals section is mandatory; every alternative gets a one-paragraph dismissal |
| Source | Generic design-doc pattern; "Design Practice Repository" (Leanpub) |

---

## CHANGELOG.md

| Field | Value |
|---|---|
| Path | `CHANGELOG.md` (some projects use `HISTORY`, `NEWS`, `RELEASES`; CHANGELOG is preferred) |
| Frontmatter | None |
| Required sections | Title, intro referencing Keep a Changelog and SemVer, `[Unreleased]` section at top |
| Optional sections | `[YANKED]` markers; per-version subsections grouped by type |
| Section order | **Fixed**: latest version first; within a version, groups appear in this order: `Added` → `Changed` → `Deprecated` → `Removed` → `Fixed` → `Security` |
| Length budget | Unbounded; oldest at bottom, newest at top |
| Validation | Each version has an ISO date `## [X.Y.Z] - YYYY-MM-DD`; yanked releases tagged `[YANKED]`; `Unreleased` section accumulates pending changes |
| Source | [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) |

---

## CONTRIBUTING.md

| Field | Value |
|---|---|
| Path | `CONTRIBUTING.md` at repo root |
| Frontmatter | None |
| Required sections | Where to ask questions, whether PRs are accepted, any PR requirements (sign-off, formatting), Code of Conduct pointer |
| Optional sections | Setup, Testing, Style, Local conventions |
| Section order | Loose |
| Length budget | < 200 lines |
| Validation | CoC linked (Contributor Covenant recommended) |
| Source | Standard contributing pattern; GitHub's "Setting up your project for healthy contributions" |

---

## .tmp/scratch

| Field | Value |
|---|---|
| Path | `.tmp/scratch/<anything>` |
| Lifetime | Per-working-tree (per `git worktree` isolation). Gitignored. |
| Commit policy | **Forbidden.** The `.tmp/` tree is gitignored. Do not even stage these paths. |
| Frontmatter | None |
| Required sections | None |
| Optional sections | Anything |
| Section order | None |
| Length budget | None |
| Validation | `.tmp/` is gitignored; deleted on worktree destroy (auto via git worktree lifecycle) |
| Source | `project-layout` skill (`.tmp/` subroles) |

---

## .tmp/migration

| Field | Value |
|---|---|
| Path | `.tmp/migration/<anything>` |
| Lifetime | Per-project. Gitignored. |
| Commit policy | **Forbidden.** This dir is never in any repo. |
| Frontmatter | None |
| Required sections | None |
| Length budget | None |
| Validation | Delete after the migration is complete and verified |
| Source | `project-layout` skill (`.tmp/` subroles) |

---

## Diátaxis quadrants

Diátaxis is **orthogonal** to filename. A single file (e.g.
`docs/how-to/foo.md`) can be misclassified as a tutorial. The matrix
below is a sanity check — what *quadrant* is your doc serving?

| Quadrant | Purpose | Length | Tone | Anti-quadrant |
|---|---|---|---|---|
| **Tutorial** | Learning by doing | As long as needed; must be end-to-end | Friendly, second-person, "we will…" | Don't explain *why*; don't offer alternatives |
| **How-to guide** | Solving a real-world problem | Short, focused on the goal | Imperative, conditional ("if you want X, do Y") | Don't teach; don't be exhaustive |
| **Reference** | Describing the machinery | Encyclopaedic, dense, neutral | Austere, factual | Don't instruct; don't explain |
| **Explanation** | Discussing a topic | As long as needed; discursive | Reflective, opinionated, "about X…" | Don't instruct; don't provide reference tables |

**Drift warning:** the most common misclassification is *tutorial that
explains*. If your how-to has paragraphs of context, it is an
explanation. If your reference has numbered steps, it is a how-to.
Re-classify before publishing.

Source: [Diátaxis](https://diataxis.fr/); [Divio — Documentation System](https://docs.divio.com/documentation-system/).