# Frontmatter Conventions

Frontmatter is the YAML block at the top of a Markdown file, fenced by
`---` lines. This document spells out which doc types **require**,
**allow**, or **forbid** frontmatter, and what fields to use when it is
allowed.

## Quick policy table

| Type | Frontmatter | Notes |
|---|---|---|
| `SKILL.md` | **Required** | `name`, `description` — enforced by `skills-ref validate` |
| Kilo rule file (`~/.config/kilo/rules/*.md`) | **Forbidden** | Global decision `kilo.rules.no_frontmatter`. Cursor convention that Kilo's loader does not parse. |
| ADR (MADR) | Optional | MADR `0013-use-yaml-front-matter-for-meta-data` |
| Knowledge-cache entry | Optional | Global rule: prefer consistent fields |
| Transient note | Optional | `task`, `status` recommended |
| Transient plan | Optional | `status`, `goal`, `last-updated` recommended |
| Persistent plan | Optional | Same as transient plan |
| RFC | Optional | `status`, `reviewers`, `deadline` recommended |
| Design doc | Optional | `status`, `last-updated` recommended |
| AGENTS.md | Forbidden | Plain Markdown only (agents.md spec) |
| README.md | Forbidden | Plain Markdown only |
| CHANGELOG.md / CONTRIBUTING.md / LICENSE | Forbidden | Plain text |
| `.tmp/scratch/*` | Forbidden | Throwaway |
| Skill reference file (`references/*.md`) | Forbidden | Only `SKILL.md` carries frontmatter |

## Required: SKILL.md frontmatter

Two fields are mandatory per the
[agentskills.io specification](https://agentskills.io/specification).
Both fields are validated by `skills-ref validate`.

### `name`

```yaml
name: document-conventions
```

Rules:

- 1–64 characters
- Lowercase letters (`a–z`), digits (`0–9`), and hyphens (`-`) only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name (the skill folder)

**Naming style.** Anthropic's best-practices guide recommends *gerund
form* (verb + `-ing`): `processing-pdfs`, `analyzing-spreadsheets`. This
skill deliberately uses the noun form `document-conventions` because the
skill is a *reference*, not a workflow. Either form is acceptable;
pick one and use it consistently across a project.

### `description`

```yaml
description: Document and filename conventions for every doc type the agent authors or edits — filename rules, frontmatter policy, section order, length budget, decision matrix, templates, checklists. Use when starting a new document, choosing between doc types (note, plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, Kilo rule, skill), validating a filename or frontmatter against the project convention, or reviewing an existing document and wondering what shape it should take. Does not own project-tree placement — for "where does this file live in a project", load the `project-layout` skill.
```

Rules:

- 1–1024 characters
- Non-empty
- No XML tags (`<` or `>`)
- Third person — *"Extracts text from PDFs"* not *"I can help with
  PDFs"* (Anthropic best-practices: descriptions are injected into the
  system prompt; inconsistent point of view breaks discovery)
- Names both **what** the skill does **and** **when** to use it
- Includes specific keywords the agent will see in the user's request

### Optional fields

```yaml
---
name: skill-name
description: What and when
license: Apache-2.0
compatibility: Requires git, docker, and internet access
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Read Write Edit Bash(git:*)
---
```

- `license` — short license name or pointer to bundled license file
- `compatibility` (≤ 500 chars) — environment requirements. Skip
  unless relevant
- `metadata` — arbitrary key/value. Use namespaced keys to avoid
  collisions (`skill.author`, not `author`)
- `allowed-tools` — **experimental**; agent implementation support
  varies

## Optional: ADR (MADR) frontmatter

Per [MADR ADR-0013](https://adr.github.io/madr/decisions/0013-use-yaml-front-matter-for-meta-data.html),
ADRs may use YAML frontmatter. Recommended fields:

```yaml
---
status: "{proposed | rejected | accepted | deprecated | superseded by ADR-NNNN}"
date: 2026-07-27
decision-makers: [alice, bob]
consulted: [carol]
informed: [engineering-team]
---
```

Status values are a controlled vocabulary. Update when the decision
changes; do not delete superseded ADRs — link forward to their
successors.

## Optional: knowledge-cache entry frontmatter

The project does not enforce fields, but the topic's `README.md`
template expects a consistent table. Recommended fields:

```yaml
---
source: https://keepachangelog.com/en/1.1.0/
captured: 2026-07-27
freshness: stable           # stable | check-2027Q2 | volatile
tags: [changelog, semver]
---
```

`freshness` tells the next agent when to re-verify. Use:

- `stable` — not expected to change for years (e.g. RFC 2119, SemVer)
- `check-<date>` — re-verify by this date (e.g. `check-2027-01`)
- `volatile` — re-verify on every use (e.g. a vendor's pricing page)

## Optional: note / plan frontmatter

Notes and plans are transient, so frontmatter is optional. Use it to
keep the title page scannable:

```yaml
---
task: shellx-export-bug
status: open                # open | captured | promoted
captured: 2026-07-27
---
```

```yaml
---
status: active              # draft | active | completed | abandoned
goal: Document conventions skill
owner: ardhinata
last-updated: 2026-07-27
---
```

## YAML syntax rules

Frontmatter uses standard YAML 1.2. Common foot-guns:

1. **Strings with colons need quoting.** `goal: Document: conventions`
   parses as `Document:` key. Use quotes:
   `goal: "Document: conventions"`.
2. **Reserved YAML keys** (`yes`, `no`, `on`, `off`, `true`, `false`,
   `null`) are coerced to booleans/null. Quote to keep as strings:
   `version: "1.0"`.
3. **Multi-line strings:** use `|` (literal) or `>` (folded). Both
   preserve newlines; `>` folds them into spaces.
4. **Indentation:** YAML forbids tabs. Use two spaces per level.
5. **Lists:** start with `- ` at the same indentation level as the
   key, not the key's value.
6. **Dates:** ISO 8601 strings parse as `date`/`datetime`. Quote if
   you want them as strings.

## Rule-file frontmatter exception

The global `~/.config/kilo/rules/*.md` files deliberately **do not**
use frontmatter (decision `kilo.rules.no_frontmatter`). Reasons:

- The loader does not parse frontmatter, so adding it is dead weight
  that drifts from the on-disk schema
- Cursor parses frontmatter as metadata; in mixed-team repos this
  creates a false expectation
- The Kilo skill loader reads SKILL.md frontmatter but treats rule
  files as plain Markdown

When in doubt for a global rule file: **omit frontmatter**. Add a
top-of-file heading (H1) instead.

## Validation

| Validator | Use for | Install |
|---|---|---|
| `skills-ref validate <dir>` | `SKILL.md` frontmatter | https://github.com/agentskills/agentskills |
| `markdownlint` | Markdown style (lists, headings) | `npm i -g markdownlint-cli` |
| `remark-lint` | Markdown style + plugins | `npm i -g remark-cli` |
| `standard-readme-preset` | `README.md` compliance | `npm i -g standard-readme-preset` |

Run the relevant validator before publishing. Treat warnings as
errors when a doc is for production use (CHANGELOG, AGENTS.md, SKILL.md,
README.md).