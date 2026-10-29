# Per-Doc-Type Conventions

The full reference for each doc type the agent creates or edits. Use this
table to confirm filename, frontmatter, sections, ordering, and length
after you pick a type from the
[decision matrix](decision-matrix.md).

## How to read this table

Each row covers one doc type. Columns:

- **Filename pattern** — exact glob. The `<…>` parts are placeholders.
- **Frontmatter** — required / optional / forbidden. Field schema if
  present.
- **Required sections** — minimum set the type *must* include.
- **Optional sections** — common additions that may appear.
- **Section order** — fixed / loose / none.
- **Length budget** — target and hard ceiling, in lines.
- **Validation** — how to verify it follows the convention.
- **Template** — the starter file, when the type ships one.
- **Source** — where the rule comes from.

## Template coverage

Fourteen of the twenty-four types ship a starter in `assets/templates/`. The
rest are deliberately template-free:

| Type | Why no template |
|---|---|
| Skill reference file | the skill template already documents the `references/` layout |
| AGENTS.md | the template lives in the `project-context` skill |
| Topic README.md, cache root README.md | the cache-topic template is the worked example of the same shape |
| Transient plan, `.tmp/scratch`, `.tmp/migration` | scratch files are never committed and have no required sections |
| Reference doc, how-to guide, Diátaxis quadrants | diataxis.fr asks for no imposed structure |
| Agent-only note | a canonical note is free-form house knowledge |

Per-type verdicts — which rules are backed by a published standard and which
are house style — are in
[`standards-map.md`](standards-map.md).

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
10. [Report (docs/reports/)](#report)
11. [Reference doc (docs/reference/)](#reference-doc)
12. [How-to guide (docs/how-to/)](#how-to-guide)
13. [Agent-only note (.agents/docs/)](#agent-only-note)
14. [Postmortem (docs/post-mortem/)](#postmortem)
15. [Persistent plan](#persistent-plan)
16. [Transient plan](#transient-plan)
17. [ADR (MADR)](#adr-madr)
18. [RFC](#rfc)
19. [Design doc](#design-doc)
20. [CHANGELOG.md](#changelogmd)
21. [CONTRIBUTING.md](#contributingmd)
22. [.tmp/scratch](#tmpscratch)
23. [.tmp/migration](#tmpmigration)
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
intent, not the filename (for example `fnm.md` not `node-version-management.md`).

---

## SKILL.md

| Field | Value |
|---|---|
| Path | `~/.agents/skills/<slug>/SKILL.md` (or project-local `.agents/skills/<slug>/`, `.<vendor>/skills/<slug>/`) |
| Frontmatter | **Required.** `name` (1–64 chars, lowercase letters/digits/hyphens, no `--`, no leading/trailing hyphen, matches parent dir), `description` (1–1024 chars, non-empty, names *what* and *when*, and should include the keywords agents search for; write it in third person — that rule comes from the Claude docs, not the spec). Optional: `license`, `compatibility` (≤ 500 chars), `metadata` (a map from string keys to string values), `allowed-tools` (a space-separated string of tool names, experimental). Claude adds two more rules the spec omits: no XML tags in either field, and no reserved words `anthropic` or `claude` in `name`. |
| Required sections | H1 (house style — the spec puts no format restriction on the body). The spec *recommends* three sections: step-by-step instructions, examples of inputs and outputs, common edge cases. |
| Optional sections | `## When to load`, `## Quick start`, `## Workflow`, `## Anti-patterns`, `## References`, `## Captured …` |
| Section order | Loose but progressive: orient → quick start → details → edge cases → anti-patterns → references |
| Length budget | Target < 300 lines; hard ceiling 500 lines. Beyond this, split into `references/*.md` |
| Validation | `skills-ref validate ./<skill-dir>` (if `skills-ref` on PATH — a Python package in the [agentskills repository](https://github.com/agentskills/agentskills/tree/main/skills-ref), for demonstration only). Manual review: frontmatter fields present, name matches dir, description in third person with key terms |
| Source | [agentskills.io specification](https://agentskills.io/specification); [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices); [Anthropic engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills); [`skill-authoring.md`](skill-authoring.md) — the house playbook for writing a skill. |

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
| Frontmatter | **Forbidden by house rule.** The [agents.md](https://agents.md/) spec mandates no fields and defines no format, so the ban is this project's choice, not the spec's. |
| Required sections | At minimum, a `Pointers` section referencing `README.md` and any skill/rule folders. Strong recommendation: `Boundaries` (`✅ Always` / `⚠️ Ask first` / `🚫 Never`). |
| Optional sections | `Purpose`, `Stack`, `Commands`, `Code style`, `Testing rules`, `Boundaries`, `Pointers` |
| Section order | Loose — the agents.md spec is free-form |
| Length budget | Target 40–80 lines, hard ceiling 150 (global rule) |
| Validation | Manual review; nested AGENTS.md overrides root when closer to edited file; closest-wins, and an explicit user chat prompt overrides everything |
| Template | [`project-context/assets/templates/agents.md`](../../project-context/assets/templates/agents.md) |
| Source | [agents.md](https://agents.md/); [project-context skill](../../project-context/SKILL.md); [Gloaguen et al., arXiv:2602.11988](https://arxiv.org/abs/2602.11988) (cost of LLM-generated context files) |

**Key rule:** every line must answer "would an agent get this wrong
without it?". Cut otherwise.

---

## README.md

| Field | Value |
|---|---|
| Path | `README.md` at repo root; `README.<lang>.md` for translations (BCP 47) |
| Frontmatter | None |
| Required sections | Title (H1), Short Description (less than 120 characters, no `>`, on its own line), Table of Contents (required unless the README is shorter than 100 lines), Install, Usage, Contributing, License — per Standard Readme. The README must not contain broken links, and its code examples must be linted the way the rest of the project lints code. English README must be `README.md`. |
| Optional sections | Banner, Badges, Long Description, Security, Extra, Background, API, Maintainers, Thanks |
| Section order | **Fixed** by Standard Readme: Title → Banner → Badges → Short Description → Long Description → ToC → Security → Background → Install → Usage → Extra → API → Maintainers → Thanks → Contributing → License |
| Length budget | Target < 200 lines; "comprehensive" 200–500. Move longer material to `docs/` |
| Validation | Standard Readme linter (`npx standard-readme`); or manual checklist in [`assets/checklists.md`](../assets/checklists.md) |
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

## Report

| Field | Value |
|---|---|
| Path | `docs/reports/<YYYY-MM-DD>-<slug>.md`, or `docs/reports/<YYYY-MM-DD>-<slug>/` with `README.md` + `NN-<section>.md` when split |
| Lifetime | Git-tracked in the project repo. |
| Commit policy | Committed with the project repo. |
| Frontmatter | Optional. Recommended: `status` (`draft`/`open`/`fixed`), `severity` (`blocker`/`major`/`minor`) |
| Required sections | H1, `## Summary`, `## Steps to reproduce`, `## Expected`, `## Actual`, `## Environment` |
| Optional sections | `## Impact`, `## Workaround`, `## Suspected cause`, `## Related` |
| Section order | Loose; the above is conventional |
| Length budget | 40–200 lines |
| Validation | Another person reproduces the problem from this file alone. The error text is exact and the version is stated. A report does not need an owner or a tracking issue, unlike a postmortem |
| Template | [`assets/templates/report.md`](../assets/templates/report.md) |
| Source | House style. The section set follows the shape of a bug report. No published standard prescribes it |

---

## Reference doc

| Field | Value |
|---|---|
| Path | `docs/reference/<slug>.md` |
| Lifetime | Git-tracked in the project repo. |
| Commit policy | Committed with the project repo. |
| Frontmatter | None |
| Required sections | H1, body |
| Optional sections | `## Prerequisites`, `## Steps`, `## Verify`, `## Troubleshooting`, `## See also` |
| Section order | Loose |
| Length budget | < 300 lines |
| Validation | Material to consult later, organised by topic rather than by task. A topic `README.md` is required once the directory holds more than one file. Linked from the doc that needs it |
| Template | None. Diátaxis asks for no imposed structure on its quadrants, so the house ships the conventions and not a template |
| Source | [Diátaxis — reference quadrant](https://diataxis.fr/reference/). The path and the filename rule are house style |

---

## How-to guide

| Field | Value |
|---|---|
| Path | `docs/how-to/<slug>.md` |
| Lifetime | Git-tracked in the project repo. |
| Commit policy | Committed with the project repo. |
| Frontmatter | None |
| Required sections | H1, body |
| Optional sections | `## Prerequisites`, `## Steps`, `## Verify`, `## Troubleshooting`, `## See also` |
| Section order | Loose |
| Length budget | < 300 lines |
| Validation | The reader completes the task without guessing. A topic `README.md` is required once the directory holds more than one file |
| Template | None. Diátaxis asks for no imposed structure on its quadrants, so the house ships the conventions and not a template |
| Source | [Diátaxis — how-to quadrant](https://diataxis.fr/how-to-guides/). The path and the filename rule are house style |

---

## Agent-only note

| Field | Value |
|---|---|
| Path | `.agents/docs/<slug>.md` |
| Lifetime | Git-tracked in the project repo. The repo-root `.agents/` tree never reaches `$HOME`. |
| Commit policy | Committed with the project repo. |
| Frontmatter | None |
| Required sections | H1, body |
| Optional sections | `## Source`, `## See also` |
| Section order | Loose |
| Length budget | < 200 lines |
| Validation | Only agent-facing content. When a human needs it, it belongs in `docs/`. No date prefix and no capture date, because a note is house knowledge rather than a dated finding |
| Template | None |
| Source | `project-layout` skill, which names `.agents/docs/` the home of agent-only docs and canonical notes |

---

## Postmortem

| Field | Value |
|---|---|
| Path | `docs/post-mortem/<YYYY-MM-DD>-<slug>.md`, or `docs/post-mortem/<YYYY-MM-DD>-<slug>/` with `README.md` + `NN-<section>.md` when split |
| Lifetime | Git-tracked in the project repo. |
| Commit policy | Committed with the project repo. |
| Frontmatter | Optional. Recommended: `severity`, `status`, `date`, `owner` |
| Required sections | H1, `## Summary`, `## Impact`, `## Root cause`, `## Timeline`, `## Action items` |
| Optional sections | `## Trigger`, `## Detection`, `## Resolution`, `## Lessons learned`, `## See also` |
| Section order | Loose; the above is conventional |
| Length budget | 50–300 lines |
| Validation | Blameless: name systems, not people. Every action item has an owner, a priority, and a tracking issue. The postmortem has one owner for the follow-up. Linked from any active runbook or related doc |
| Template | [`assets/templates/postmortem.md`](../assets/templates/postmortem.md) |
| Source | [Google SRE — Example Postmortem](https://sre.google/sre-book/example-postmortem/); [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/); [PagerDuty postmortem template](https://response.pagerduty.com/after/post_mortem_template/) |

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
| Frontmatter | Optional. Recommended: `status` (`proposed`/`rejected`/`accepted`/`deprecated`/`superseded by ADR-NNNN`), `date`, `decision-makers`, `consulted`, `informed`. MADR leaves the status set open — its own placeholder ends in `…`, and ADR-0008 shows free-form values such as `on hold`. The house rule narrows it to the five values above. |
| Required sections | Title, `## Context and Problem Statement`, `## Considered Options`, `## Decision Outcome` |
| Optional sections | `## Decision Drivers`, `### Consequences` (Good/Bad/Neutral), `### Confirmation`, `## Pros and Cons of the Options` (per option), `## More Information` |
| Section order | **MADR order** (house-tightened to fixed): Title → Context → Drivers → Considered Options → Decision Outcome → Consequences → Confirmation → Pros/Cons → More Info. MADR marks all but the first three optional and ships minimal and bare variants. |
| Length budget | 50–200 lines |
| Validation | Numbering without gaps; status field present and accurate; superseded ADRs reference their successor |
| Template | [`assets/templates/adr.md`](../assets/templates/adr.md) |
| Source | [MADR](https://adr.github.io/madr/); [adr.github.io](https://adr.github.io/); Nygard 2011 "Documenting Architecture Decisions" |

---

## RFC

| Field | Value |
|---|---|
| Path | `docs/rfcs/NNNN-<slug>.md`, or `docs/rfcs/NNNN-<slug>/` with `README.md` + `NN-<section>.md` when split |
| Frontmatter | Optional. Recommended: `status` (`draft`/`review`/`accepted`/`rejected`/`withdrawn`), `reviewers`, `deadline`, `last-updated` |
| Required sections | H1 (slug title), `## Summary`, `## Motivation`, `## Detailed design`, `## Drawbacks`, `## Alternatives`, `## Unresolved questions` |
| Optional sections | `## Prior art`, `## Future possibilities`, `## Implementation plan`, `## Acknowledgements`, `## Open questions` |
| Section order | Loose; the section list is house style, modelled on the Rust and React RFC templates |
| Length budget | 200–1000 lines |
| Validation | Reviewers listed; deadline set; status updated when feedback closes |
| Template | [`assets/templates/rfc.md`](../assets/templates/rfc.md) |
| Source | [Rust RFC template](https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md); [React RFC template](https://raw.githubusercontent.com/reactjs/rfcs/main/0000-template.md). RFC 2119 and 8174 govern requirement-keyword casing only, not document structure. |

---

## Design doc

| Field | Value |
|---|---|
| Path | `docs/design/<slug>.md`, or `docs/design/<slug>/` with `README.md` + `NN-<section>.md` when split |
| Frontmatter | Optional. Recommended: `status`, `last-updated` |
| Required sections | H1, `## Problem`, `## Goals / non-goals`, `## Proposed design`, `## Alternatives considered` |
| Optional sections | `## Open questions`, `## Implementation plan`, `## Testing`, `## Risks`, and the security, privacy, internationalization and storage subsections the Google guidance expects |
| Section order | Loose |
| Length budget | 500–2000 lines |
| Validation | Goals/non-goals section is mandatory; every alternative gets a one-paragraph dismissal; security, privacy, internationalization and storage are each answered |
| Template | [`assets/templates/design-doc.md`](../assets/templates/design-doc.md) |
| Source | [Software Engineering at Google, ch.10 — Documentation](https://abseil.io/resources/swe-book/html/ch10.html); [Kubernetes KEP template](https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md) |

---

## CHANGELOG.md

| Field | Value |
|---|---|
| Path | `CHANGELOG.md` (some projects use `HISTORY`, `NEWS`, `RELEASES`; CHANGELOG is preferred) |
| Frontmatter | None |
| Required sections | Title, intro referencing Keep a Changelog and SemVer, `[Unreleased]` section at top |
| Optional sections | `[YANKED]` markers; per-version subsections grouped by type |
| Section order | Latest version first. Within a version, the house order is `Added` → `Changed` → `Deprecated` → `Removed` → `Fixed` → `Security`. Keep a Changelog only asks for same-type grouping, so the fixed order is house policy. |
| Length budget | Unbounded; oldest at bottom, newest at top |
| Validation | Each version has an ISO date `## [X.Y.Z] - YYYY-MM-DD` (the spec calls this format recommended, not required); yanked releases tagged `[YANKED]`; `Unreleased` section accumulates pending changes |
| Template | [`assets/templates/changelog.md`](../assets/templates/changelog.md) |
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
| Template | [`assets/templates/contributing.md`](../assets/templates/contributing.md) |
| Source | No published CONTRIBUTING.md template exists. [opensource.guide — contributing guidelines](https://opensource.guide/starting-a-project/#writing-your-contributing-guidelines); [GitHub — Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions) |

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

Diátaxis is **orthogonal** to filename. A single file (for example
`docs/how-to/foo.md`) can be misclassified as a tutorial. The matrix
below is a sanity check — what *quadrant* is your doc serving?

| Quadrant | Purpose | Length | Tone | Anti-quadrant |
|---|---|---|---|---|
| **Tutorial** | Learning by doing | As long as needed; must be end-to-end | Friendly, first-person plural ("we will…") | Don't explain *why*; don't offer alternatives |
| **How-to guide** | Solving a real-world problem | Short, focused on the goal | Imperative, conditional ("if you want X, do Y") | Don't teach; don't be exhaustive |
| **Reference** | Describing the machinery | No length rule in Diátaxis | Austere, neutral, objective, factual | Don't instruct; don't explain |
| **Explanation** | Discussing a topic | As long as needed; discursive | Reflective, opinionated, "about X…" | Don't instruct; don't provide reference tables |

Diátaxis publishes language rules, not templates, and asks for no imposed
structure. No quadrant template ships with this skill.

The house paths for two of the quadrants are defined above: the
[reference doc](#reference-doc) at `docs/reference/` and the
[how-to guide](#how-to-guide) at `docs/how-to/`. This section decides which
quadrant a document serves. Those two sections decide where it lives.

**Drift warning:** the most common misclassification is *tutorial that
explains*. If your how-to has paragraphs of context, it is an explanation.
If your reference contains numbered steps, it is a how-to. The other axis Diátaxis
calls the most common conflation is study versus work: a tutorial is
learning-oriented, a how-to is task-oriented. Re-classify before publishing.

Source: [Diátaxis](https://diataxis.fr/). [Divio — Documentation System](https://docs.divio.com/documentation-system/).