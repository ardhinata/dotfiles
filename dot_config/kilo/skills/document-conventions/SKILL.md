---
name: document-conventions
description: Document conventions and authoring standards for every doc type the agent creates or edits — AGENTS.md, README.md, SKILL.md, Kilo rule files, knowledge-cache entries, plans, notes, ADRs, RFCs, CHANGELOG, scratch files. Use when starting a new document, choosing between doc types, validating naming or frontmatter, or aligning structure to project and open-spec rules. Loads decision matrix + per-type tables; ignores files in `.gitignore`; never edits encrypted secrets.
---

# Document Conventions

A unified reference for every document type the agent authors or edits. Each
type has a known **filename pattern**, a **frontmatter policy**, a **section
order** (when one is mandated), and a **length budget**. The goal is
consistent structure across the repo without re-inventing the wheel on
every new doc.

## When to load

- Picking the right doc type for a new task ("should this be a note, a plan,
  an ADR, or a knowledge-cache entry?"). Start with the
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
| [`assets/checklists.md`](assets/checklists.md) | Per-type pre-publish checklist |
| [`assets/templates/`](assets/templates/) | Starter templates for each doc type |

## The decision matrix (quick view)

The full version is in [`references/decision-matrix.md`](references/decision-matrix.md).

| You want to… | Write |
|---|---|
| Capture a verified, non-obvious, reusable finding during a task | **Note** — `.tmp/notes/<YYYY-MM-DD>-<task-slug>.md` |
| Plan a multi-step task that may not survive compaction | **Transient plan** — `.tmp/plans/<YYYY-MM-DD>-<task-slug>.md` |
| Plan a multi-step task the user wants to keep | **Persistent plan** — user-specified path |
| Document a decision with options and consequences | **ADR** — `docs/adr/NNNN-<slug>.md` |
| Propose a large design for review | **RFC** — `docs/rfcs/NNNN-<slug>.md` |
| Cache a reusable web-learned fact | **Knowledge-cache entry** — `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` |
| Encode a repo-wide rule the agent must follow every session | **Kilo rule file** — `dot_config/kilo/rules/<slug>.md` |
| Package a workflow the agent loads on demand | **Skill** — `dot_config/kilo/skills/<slug>/SKILL.md` (with frontmatter) |
| Introduce the project to humans | **README.md** |
| Encode project conventions for agents | **AGENTS.md** (closest to file wins) |
| Introduce a doc subtree | **topic README.md** |
| Record release-by-release changes | **CHANGELOG.md** |
| Document contribution workflow | **CONTRIBUTING.md** |
| Park throwaway work | **`.tmp/scratch/...`** — no convention beyond "delete when done" |

## Universally applicable rules

These rules apply to **every** doc type unless the per-type reference says
otherwise:

1. **Plain Markdown.** No HTML except where Markdown genuinely cannot
   express something (e.g. `<details>` for collapsible sections).
2. **Forward slashes** in file paths, even on Windows (`reference/foo.md`,
   not `reference\foo.md`). Required by the agentskills.io runtime.
3. **ISO 8601 dates** (`YYYY-MM-DD`) for any date in filenames or headings.
   `YYYY-MM-DD` sorts lexicographically and is unambiguous across locales
   (Keep a Changelog §"Confusing Dates").
4. **Lowercase, hyphenated slugs.** Lowercase a–z, digits, hyphens. No
   spaces, underscores, capitals, or special chars in filenames. Hyphens
   are the word separator; *never* use underscores or camelCase in
   filenames. **This applies only to files where *you* choose the name.**
   Established stems (`README.md`, `AGENTS.md`, `CHANGELOG.md`,
   `LICENSE`), tool-fixed names (`Makefile`, `Dockerfile`,
   `package.json`), and project prefixes (`dot_*`, `executable_*`,
   `*.tmpl`) keep their widely-recognised form. See
   [title-and-filename.md § Principle](references/title-and-filename.md#principle-use-the-right-convention-for-the-file-type).
5. **Relative links** between docs in the same repo. Relative links keep
   the relationship working on clones and in editors. Use absolute URLs
   only for external sources.
6. **One H1 per file**, equal to (or near-equal to) the filename slug.
   Avoid numbering in H1s (MADR ADR-0002).
7. **No frontmatter unless the per-type policy says to use it.** Two
   exceptions: `SKILL.md` (mandatory) and ADRs (optional but
   recommended). The project's `dot_config/kilo/rules/*.md` files
   explicitly **do not** use frontmatter (see
   [frontmatter § project rule files](references/frontmatter.md)).
8. **Be conservative with structure.** Pick the lightest convention that
   fits. Avoid adding sections "for completeness". The user's task is the
   source of truth; the doc shape serves it.
9. **No secrets.** Tokens, private keys, fingerprints, passwords, and
   recovery phrases never go in docs. If a finding requires mentioning
   one, point to the encrypted file and stop.

## Filename quick reference

| Pattern | Type |
|---|---|
| `AGENTS.md` | Project agent guide (root or nested) |
| `README.md` | Human-facing project intro / topic intro |
| `CONTRIBUTING.md` | Contribution workflow |
| `CHANGELOG.md` | Release-by-release change log |
| `LICENSE` | License file |
| `.tmp/notes/<YYYY-MM-DD>-<task-slug>.md` | Transient task note |
| `.tmp/plans/<YYYY-MM-DD>-<task-slug>.md` | Transient plan |
| `.tmp/scratch/<anything>` | Throwaway scratch (gitignored) |
| `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` | Knowledge-cache entry |
| `.agents/docs/cache/<topic>/README.md` | Topic README (cache index) |
| `.agents/docs/cache/README.md` | Cache root index |
| `dot_config/kilo/rules/<slug>.md` | Kilo rule file |
| `dot_config/kilo/skills/<slug>/SKILL.md` | Skill main file |
| `dot_config/kilo/skills/<slug>/references/*.md` | Skill reference file |
| `docs/adr/NNNN-<slug>.md` | MADR-style ADR |
| `docs/rfcs/NNNN-<slug>.md` | RFC |
| `docs/design/<slug>.md` | Design doc |
| `docs/plans/<slug>.md` | Persistent plan (user-specified) |
| `docs/how-to/<slug>.md` | How-to guide |
| `docs/reference/<slug>.md` | Reference guide |

Full schemas are in [`references/by-doc-type.md`](references/by-doc-type.md).

## Frontmatter quick reference

| Type | Frontmatter? |
|---|---|
| Kilo rule file (`dot_config/kilo/rules/*.md`) | **Forbidden** (project decision) |
| SKILL.md | **Required** — `name` + `description` |
| ADR (MADR) | Optional but recommended — `status`, `date`, `decision-makers` |
| Knowledge-cache entry | Optional — `source`, `captured`, `freshness` |
| Persistent plan | Optional — `status`, `owner`, `last-updated` |
| Note (`.tmp/notes/`) | Optional — `task`, `status` |
| README.md / CHANGELOG.md / CONTRIBUTING.md | No |
| AGENTS.md | No |
| Scratch | No |

See [`references/frontmatter.md`](references/frontmatter.md) for full field
schemas and YAML rules.

## Workflow

1. **Pick the type.** Use the decision matrix above. If a task needs
   *both* persistence and searchability, an ADR captures the why; a
   knowledge-cache entry captures the what.
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

## Captured sources

These rules are synthesised from:

- [agents.md — open format](https://agents.md/) (LF/AAIF, Dec 2025)
- [agentskills.io — specification](https://agentskills.io/specification) (Anthropic, Oct 2025)
- [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Equipping agents for the real world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) (community, 6.3k★)
- [Divio — The Documentation System](https://docs.divio.com/documentation-system/) (canonical four quadrants)
- [Diátaxis](https://diataxis.fr/) (canonical four quadrants, language rules)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [MADR — Markdown Any Decision Records](https://adr.github.io/madr/)
- [adr.github.io — decision records](https://adr.github.io/)
- [Andy Matuschak — Evergreen notes](https://notes.andymatuschak.org/Evergreen_notes)
- Project rules: `dot_config/kilo/rules/*.md` and the global
  `~/.config/kilo/rules/*.md` (proactive-note-capture, personal-quirks,
  web-tools-priority, project-context, self-analysis, ambiguity-resolution)
- Project decision `kilo.rules.no_frontmatter` — rule files have no
  frontmatter even though skills do

Re-verify before relying on exact field limits in 2027+. Volatility is high
for skill/agents.md specs (< 12 months old); low for Keep a Changelog,
SemVer, MADR, Diátaxis, Conventional Commits.

## Anti-patterns (top three)

Full list in [`references/anti-patterns.md`](references/anti-patterns.md).
The three most common:

1. **Adding sections "just in case".** README/AGENTS.md files balloon past
   their length budget and become noise. Cut anything that does not pass
   "would an agent get this wrong without this line?".
2. **Frontmatter drift.** Some types require it (SKILL.md), some forbid it
   (project rule files), most are neutral. Do not copy frontmatter from
   one type to another.
3. **Linking by absolute path or external URL inside the repo.** Use
   relative links so the docs survive clones, moves, and editor
   renames.