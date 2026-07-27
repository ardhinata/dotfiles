# Title and Filename Conventions

How to name files and write the H1 inside them. Filenames and titles
together drive discoverability, sort order, and tooling compatibility.

## Filename rules (universal)

These rules apply to every doc type unless a per-type rule says
otherwise:

1. **Lowercase a–z, digits, hyphens only.** No spaces, no underscores, no
   capitals. Hyphens are the word separator; *never* use underscores or
   camelCase in filenames.
2. **No leading or trailing hyphens.** Filenames don't start or end
   with `-`. Avoid consecutive `--`.
3. **No file extension beyond `.md`** (or `.markdown`). `.md` is the
   project default.
4. **ASCII only.** Avoid non-ASCII characters in filenames even when
   the topic supports them — `cafe.md`, not `café.md`.
5. **Forward slashes for path separators** (`reference/foo.md`, not
   `reference\foo.md`). Required by the agentskills.io runtime.
6. **Match the slug to the topic**, not the author, not the date. Date
   prefixes live outside the slug (see date rules below).

## Date rules

Three patterns appear, by doc type:

### ISO date prefix — knowledge-cache entries, notes, plans

Pattern: `YYYY-MM-DD-<slug>.md`

- **Why ISO 8601:** sorts lexicographically; unambiguous across locales
  (Keep a Changelog §"Confusing Dates").
- **Where the date goes:** at the start of the filename, separated by
  `-`. The date *is* part of the filename, not the slug.
- **Same-day collisions:** append a counter, e.g.
  `2026-07-27-foo-2.md`. Avoid this by scanning `.tmp/notes/` (or the
  cache) before creating.

### Numbered prefix — ADRs, RFCs

Pattern: `NNNN-<slug>.md`

- **4-digit zero-padded sequence.** MADR allows up to 9999 ADRs in one
  directory.
- **Sequencing is stable.** Don't renumber existing files when adding
  new ones; always append. MADR ADR-0002: "do not use numbers in
  headings" — the number is in the filename, not the H1.
- **Monorepos / categories:** MADR allows subdirectories per category
  (`docs/adr/backend/0001-foo.md`); sequence restarts within each
  category but the file is still uniquely identified by full path.

### No date — most other types

README.md, CHANGELOG.md, CONTRIBUTING.md, AGENTS.md, Kilo rule files,
skill `SKILL.md`, design docs, how-to guides, topic READMEs — none of
these carry a date in their filename. The repo or release owns the
versioning.

## Slug rules (universal)

A slug is the lowercase-hyphenated form of a phrase. Examples:

- "How to deploy to Kubernetes" → `how-to-deploy-to-kubernetes.md`
- "FNM Node Manager" → `fnm-node-manager.md` (or `fnm.md` if your repo
  has only one such file)
- "Rename `_draft` to `draft/`" → don't slug this; the topic is
  "directory renames"

Slug heuristics:

- **Drop articles and prepositions** in long titles when the meaning
  is preserved (`how-to-configure-foo`, not `how-to-configure-the-foo`).
- **Drop "the", "a", "an"** unless removing them changes meaning.
- **Avoid stop-words at the end** (`-the`, `-and`, `-or`).
- **Keep the slug ≤ 60 chars** when possible.
- **Match the H1.** The H1 inside the file should be the human-readable
  form of the slug (`# How to configure foo` ↔ `how-to-configure-foo.md`).

## H1 rules

Every file should have **exactly one H1**, written in sentence case.

| Doc type | H1 form |
|---|---|
| Skill SKILL.md | Title Case, matches `name` field (`# Document Conventions`) |
| AGENTS.md | Sentence case, project name (`# My Project`) |
| README.md | Sentence case, project or topic name |
| Kilo rule file | Sentence case, rule summary (`# Proactive Note Capture`) |
| Note | Sentence case, finding summary (`# Shellx slug derivation`) |
| Plan | Sentence case, task summary (`# Document conventions skill — research and draft`) |
| ADR | Title Case, the solved problem (`# Use Plain JUnit5 for advanced test assertions`) |
| Knowledge-cache entry | Sentence case, finding summary |
| CHANGELOG.md | `# Changelog` (per Keep a Changelog) |
| CONTRIBUTING.md | `# Contributing` |

**No numbering in H1s** (MADR ADR-0002). The ADR filename carries the
number; the H1 does not.

## Per-type filename patterns (summary)

The full table is in [`by-doc-type.md`](by-doc-type.md). Quick reference:

```
AGENTS.md
README.md
README.<lang>.md                          # BCP 47 translation
CHANGELOG.md
CONTRIBUTING.md
LICENSE

.tmp/notes/<task-slug>-YYYY-MM-DD.md
.tmp/plans/<task-slug>-YYYY-MM-DD.md
.tmp/scratch/<anything>                   # no convention

.agents/docs/cache/README.md
.agents/docs/cache/<topic>/README.md
.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md

dot_config/kilo/rules/<slug>.md
dot_config/kilo/skills/<slug>/SKILL.md
dot_config/kilo/skills/<slug>/references/<slug>.md

docs/adr/NNNN-<slug>.md
docs/rfcs/NNNN-<slug>.md
docs/design/<slug>.md
docs/how-to/<slug>.md
docs/reference/<slug>.md
docs/explanation/<slug>.md
docs/plans/<slug>.md
docs/<topic>/README.md
```

## Filename-to-topic rules

Some filename stems have widely understood meanings. Use them
consistently across the repo:

| Stem | Meaning |
|---|---|
| `README.md` | Human-facing intro / topic index |
| `AGENTS.md` | Agent guide |
| `CHANGELOG.md` | Release-by-release change log |
| `CONTRIBUTING.md` | Contribution workflow |
| `LICENSE` | License file (no extension) |
| `CODE_OF_CONDUCT.md` | Code of conduct |
| `SECURITY.md` | Security disclosure policy |
| `SUPPORT.md` | Where to get help |
| `TODO.md` | High-level TODO list (rare, prefer issues) |
| `ROADMAP.md` | Forward-looking plan (rare) |
| `FAQ.md` | Frequently asked questions |

Do not invent new stems (`NOTES.md`, `MEMOS.md`, etc.) when one of the
above will do.

## File naming exceptions

- **`<name>.tmpl`** — chezmoi template. The agent may need to render
  the file before reading. See [`chezmoi` skill](../../../../../.agents/kilo/skills/chezmoi/SKILL.md).
- **`executable_*`** — chezmoi-conventional executable files. Drop the
  `executable_` prefix when chezmoi applies the file. See
  [`chezmoi` skill](../../../../../.agents/kilo/skills/chezmoi/SKILL.md).
- **`dot_*`** — chezmoi-conventional "hidden" files. The prefix maps to
  the dot (e.g. `dot_config/` → `~/.config/`). See
  [`chezmoi` skill](../../../../../.agents/kilo/skills/chezmoi/SKILL.md).