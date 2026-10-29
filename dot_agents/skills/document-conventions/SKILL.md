---
name: document-conventions
description: Use when starting a new document, authoring or revising a SKILL.md, choosing between doc types (plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, rule file, skill, report, reference doc, how-to guide), validating a filename or frontmatter against the project convention, or reviewing an existing document. Gives the filename rules, frontmatter policy, section order, length budget, decision matrix, templates, and checklists for each doc type. Does not own project-tree placement — for "where does this file live in a project", load the `project-layout` skill. For prose clarity in the body of the document (active voice, one idea per sentence, plain words), load the `asd-ste100` skill.
---

# Document Conventions

A unified reference for every document type the agent authors or edits. Each
type has a known **filename pattern**, a **frontmatter policy**, a **section
order** (when one is mandated), and a **length budget**. The goal is
consistent structure across the repo without re-inventing the wheel on
every new doc.

## Standard vs house style

This skill mixes two things. Know which is which before you cite one.

**Backed by a published standard or convention:**

| Rule | Source |
|---|---|
| `SKILL.md` frontmatter (`name` + `description` limits) | agentskills.io specification |
| Third-person `description`, no XML tags, no reserved words | Claude skill authoring best practices |
| ADR frontmatter, optional | MADR template |
| One H1 per page | Google style guide, headings. markdownlint MD025 only forbids a *second* H1; it cannot enforce exactly one. |
| Lowercase hyphenated filenames, known stems exempt | Google filenames guide, agentskills.io `name` field. Google allows underscores for directory consistency; this skill does not. |
| ISO 8601 dates | ISO 8601, Keep a Changelog |
| Forward slashes in paths | Claude skill authoring best practices |
| Relative links between docs in one repo | GitLab style guide |
| No secrets in docs | GitLab style guide, "Fake tokens"; GitHub, "Removing sensitive data from a repository" |
| "Pick the lightest convention that fits" | agentskills.io best practices, Diátaxis |
| Intent → document-type matrix | the Diátaxis compass pattern |
| `NNNN-<slug>.md` for ADRs and RFCs | MADR, Rust RFC template |
| README section order | Standard Readme spec |
| CHANGELOG categories, `[YANKED]`, date format | Keep a Changelog 1.1.0 |
| Blameless postmortem, action-item owner and tracking issue | Google SRE postmortem culture |
| Design doc: goals, trade-offs, alternatives | Software Engineering at Google, ch.10 |

For the per-type verdicts, and the list of citations that were wrong, read
[`references/standards-map.md`](references/standards-map.md).

**House style.** No external standard covers these. They are this project's
conventions — internally consistent, but cite them as house style, not as
industry practice:

- The four invented doc types: **persistent plan**,
  **knowledge-cache entry**, **rule file**, **scratch file**
- Every per-type length budget (all numbers in
  [structure-and-length.md](references/structure-and-length.md))
- The frontmatter matrix — which types require, forbid, or tolerate it
- Tightenings applied on top of a standard: the closed ADR status set, the
  fixed CHANGELOG category order, the ban on underscores in filenames
- The "rule file carries no frontmatter" rule. This is a project decision.
  Cursor's `.mdc` convention requires frontmatter, but no rule loader
  parses it.
- The date-prefixed filename convention for notes and plans

**Harness config directory.** Paths written `~/.config/<vendor>/…` below mean the
harness's user-level config directory: `~/.config/opencode/` in OpenCode.
Skills live in the shared home `~/.agents/skills/`, which most harnesses read.
Harness-neutral rules live in the shared home `~/.agents/rules/`. No harness
discovers that directory on its own: each one loads it through its own
`instructions` glob. A rule that names one harness's tool belongs in that
harness's own rule tree, `dot_agents/exact_rules.<vendor>/`, deployed to
`~/.agents/rules.<vendor>/`. The `project-layout` skill owns the canonical
tree.

## When to load

- Picking the right doc type for a new task ("should this be a plan, an ADR,
  or a knowledge-cache entry?"). Start with the
  [decision matrix](references/decision-matrix.md).
- Starting a new document. Use the
  [by-doc-type](references/by-doc-type.md) table for the type's required
  filename, frontmatter, and section order.
- Validating a file against the project's convention. Use the
  [checklists](assets/checklists.md).
- Reviewing an existing document and wondering what shape it should take.
- Answering "what does X mean?" questions like "do our rule files use
  frontmatter?" — see [frontmatter](references/frontmatter.md).

Do **not** load just to read a doc the agent already understands. Load it
when a *structural* or *naming* decision is on the table.

## How this skill is organised

The body of `SKILL.md` is a short orientation. Detail lives one level deep
in `references/` so the agent can pull only what it needs (per the
[agentskills.io spec](https://agentskills.io/specification) on progressive
disclosure).

| File | When to read |
|---|---|
| [`references/decision-matrix.md`](references/decision-matrix.md) | Choosing *what kind* of doc to write |
| [`references/by-doc-type.md`](references/by-doc-type.md) | The full per-type tables (filename, frontmatter, sections, length) |
| [`references/title-and-filename.md`](references/title-and-filename.md) | Slug rules, date formats, numbering, case, and when **not** to apply kebab-case |
| [`references/frontmatter.md`](references/frontmatter.md) | Frontmatter policies per type, YAML rules, exceptions |
| [`references/structure-and-length.md`](references/structure-and-length.md) | Required sections, ordering, length budgets |
| [`references/cross-references.md`](references/cross-references.md) | Linking style, anchors, path citations |
| [`references/anti-patterns.md`](references/anti-patterns.md) | Do/don't checklist, common mistakes |
| [`references/skill-authoring.md`](references/skill-authoring.md) | Writing a `SKILL.md` that earns its context budget |
| [`references/standards-map.md`](references/standards-map.md) | Which rules are standard, which are house style, which citations were wrong |
| [`assets/checklists.md`](assets/checklists.md) | Per-type pre-publish checklist |
| [`assets/templates/`](assets/templates/) | Starter templates for each doc type, plus the split-doc directory index |

## The decision matrix

Read [`references/decision-matrix.md`](references/decision-matrix.md) to pick
the doc type. It holds the full matrix and the heuristics for ambiguous
pairs.

> **Filename collisions:** date-prefixed names sort chronologically but can
> collide on the same day. Scan the target directory before writing and
> append a counter (`-2`, `-3`) when needed.

## When a doc is too big

A doc over its hard ceiling splits into a **directory**: an index
`README.md` plus numbered section files `NN-<section-slug>.md`. The
directory name is the slug the single file would have had.

Use a directory for one long subject. Use separate linked docs when the
content holds several subjects. See
[structure-and-length.md](references/structure-and-length.md#when-a-doc-outgrows-its-file)
for the full rule and the types that may split.

## Universally applicable rules

These rules apply to **every** doc type unless the per-type reference says
otherwise:

1. **Plain Markdown.** No HTML except where Markdown genuinely cannot
   express something (for example `<details>` for collapsible sections), and HTML
   comments used as notes to the author.
2. **Forward slashes** in file paths, even on Windows (`reference/foo.md`,
   not `reference\foo.md`). The agentskills.io spec asks for relative paths
   from the skill root. Forward slashes are the cross-platform form of that.
3. **ISO 8601 dates** (`YYYY-MM-DD`) for any date in filenames or headings.
   `YYYY-MM-DD` sorts lexicographically and is unambiguous across locales
   (Keep a Changelog §"Confusing Dates").
4. **Lowercase, hyphenated slugs.** Lowercase a–z, digits, hyphens. No
   spaces, underscores, capitals, or special chars in filenames. Hyphens
   are the word separator. *Never* use underscores or camelCase in
   filenames. Google allows underscores when a directory already uses them
   for consistency. This skill does not. **This applies only to files where
   *you* choose the name.**
   Established stems (`README.md`, `AGENTS.md`, `CHANGELOG.md`,
   `LICENSE`), tool-fixed names (`Makefile`, `Dockerfile`,
   `package.json`), and project prefixes (`dot_*`, `executable_*`,
   `*.tmpl`) keep their widely-recognised form. See
   [title-and-filename.md § Principle](references/title-and-filename.md#principle-use-the-right-convention-for-the-file-type).
5. **Relative links** between docs in the same repo. Relative links keep
   the relationship working on clones and in editors. Use absolute URLs
   only for external sources.
6. **One H1 per file.** Derive the title from the filename's words, in
   sentence case. Avoid numbering in H1s (MADR ADR-0002).
7. **No frontmatter unless the per-type policy says to use it.** Two
   exceptions: `SKILL.md` (mandatory) and ADRs (optional but
   recommended). The global `~/.agents/rules/*.md` files
   explicitly **do not** use frontmatter (see
   [frontmatter § global rule files](references/frontmatter.md)).
8. **Be conservative with structure.** Pick the lightest convention that
   fits. Avoid adding sections "for completeness". The user's task is the
   source of truth. The doc shape serves it.
9. **No secrets.** Tokens, private keys, fingerprints, passwords, and
   recovery phrases never go in docs. If a finding requires mentioning
   one, point to the encrypted file and stop.

## Filename and frontmatter

[`references/by-doc-type.md`](references/by-doc-type.md) holds the full
per-type tables for filenames, frontmatter, required sections, and length
budgets. [`references/frontmatter.md`](references/frontmatter.md) holds the
frontmatter policies and the YAML rules.

## Workflow

1. **Pick the type.** Read
   [`references/decision-matrix.md`](references/decision-matrix.md). If a task
   needs *both* persistence and searchability, an ADR captures the why.
   A knowledge-cache entry captures the what.
2. **Use the template.** Every doc type has a starter in
   `assets/templates/`. Copy, rename, fill.
3. **Validate.** Run the per-type checklist from
   `assets/checklists.md`. For `SKILL.md`, also run
   `skills-ref validate ./<skill-dir>` if the binary is on PATH.
4. **Update indexes.** If you wrote a knowledge-cache entry, add a
   relative link to the topic's `README.md` (and to the root index if
   the topic is new).
5. **Self-review against anti-patterns.** See
   [`references/anti-patterns.md`](references/anti-patterns.md). The most
   common drift: padding length, adding sections "just in case",
   duplicating content that already lives elsewhere.
6. **Style pass.** Run the `asd-ste100` skill's Scan Checklist
   over the prose (synonym rotation, hedge stacking, nominalization,
   marketing adjectives, run-on sentences, soft phrasal verbs). This
   skill owns *shape*. `asd-ste100` owns *clarity*. Apply it before
   emitting the doc — no human is in the loop afterward to disambiguate.

## Captured sources

These rules are synthesised from:

- [agents.md — open format](https://agents.md/) (LF/AAIF, Dec 2025)
- [agentskills.io — specification](https://agentskills.io/specification) (Anthropic, Oct 2025)
- [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Equipping agents for the real world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) (community, 6.3k★)
- [Diátaxis](https://diataxis.fr/) (canonical four quadrants, language rules)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) (commit-message format — relevant to CHANGELOG generation, not to document shape)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [MADR — Markdown Any Decision Records](https://adr.github.io/madr/)
- [adr.github.io — decision records](https://adr.github.io/)
- [Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
- [Google SRE — Example Postmortem](https://sre.google/sre-book/example-postmortem/)
- [Software Engineering at Google, ch.10 — Documentation](https://abseil.io/resources/swe-book/html/ch10.html)
- [Andy Matuschak — Evergreen notes](https://notes.andymatuschak.org/Evergreen_notes)
- Global rules: `~/.agents/rules/*.md` (web-verification, project-context,
  local-first, ambiguity-resolution, long-running-tools, document-conventions)
  + per-user rules at `~/.agents/rules.personal.d/*.md` (sudo-ask,
  ssh-read-allowlist, ssh-agent-keys-location)
- Project decision — rule files carry no frontmatter even though skills do

Re-verify before relying on exact field limits in 2027+. Volatility is high
for skill/agents.md specs (< 12 months old). It is low for Keep a Changelog,
SemVer, MADR, Diátaxis, Conventional Commits.

## Anti-patterns (top three)

Full list in [`references/anti-patterns.md`](references/anti-patterns.md).
The three most common:

1. **Adding sections "just in case".** README/AGENTS.md files balloon past
   their length budget and become noise. Cut anything that does not pass
   "would an agent get this wrong without this line?".
2. **Frontmatter drift.** Some types require it (SKILL.md), some forbid it
   (global rule files), most are neutral. Do not copy frontmatter from
   one type to another.
3. **Linking by absolute path or external URL inside the repo.** Use
   relative links so the docs survive clones, moves, and editor
   renames.