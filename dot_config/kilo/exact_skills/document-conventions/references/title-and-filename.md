# Title and Filename Conventions

How to name files and write the H1 inside them. Filenames and titles
together drive discoverability, sort order, and tooling compatibility.

## Principle: use the right convention for the file type

The rules below describe how to name a file *when you are choosing the
name yourself*. Many filenames are **fixed by widely-recognised
conventions** that already exist outside this skill — kebab-case
(lowercase + hyphens) is the *slug convention*, not a universal
filename rule.

### One case system vs. context-appropriate

The research consensus is that **"one case system everywhere" is a
false goal**. Even within a single language, multiple cases are common
(`camelCase` for variables and functions, `PascalCase` for classes in
Java / TypeScript / C#). Authoritative style guides therefore delegate
the choice to the surrounding context:

- **Google C++ Style Guide — File Names**: *"Filenames should be all
  lowercase and can include underscores (`_`) or dashes (`-`). **Follow
  the convention that your project uses.** If there is no consistent
  local pattern to follow, prefer `_`."*
- **Google developer documentation style guide — Filenames**: *"If
  you're adding to a directory where everything else already uses
  underscores, and it's not feasible to change everything to hyphens,
  **it's okay to use underscores to stay consistent.**"*
- **Devopedia — Naming Conventions**: *"there's no single one that fits
  all scenarios. Each programming language recommends its own
  convention. … When a project is written in multiple languages, it's
  not possible to have a single naming convention. For each language,
  adopt the naming convention prevalent in that language."*
- **ITU Online — Programming Case Styles**: *"There is no universal
  winner among the programming cases types. The right choice is the
  one that fits the ecosystem and matches the surrounding codebase."*

In short: **the case system follows the context** (language,
ecosystem, tool, or project), not the other way around. "Use
kebab-case for everything" is a popular heuristic, but applying it
blindly to filenames like `README.md`, `Makefile`, or `package.json`
creates friction that no style guide recommends.

### The four layers of filename conventions

Pick the convention that matches the file type, in this order:

1. **Established filename stems** (community-wide). `README.md`,
   `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`,
   `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `FAQ.md` — these
   names are recognised by every tool, platform, and reader. Renaming
   them to `readme.md`, `agents-guide.md`, or `changelog-of-releases.md`
   would be a regression even though those names *technically* follow
   the slug rules. The "Filename-to-topic rules" table below codifies
   this list; do not invent new stems when one of them will do.
2. **Domain-standard names** (tool-specific). `Makefile`, `Dockerfile`,
   `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`,
   `.gitignore`, `.env`, `tsconfig.json` — tool-specific filenames are
   fixed by the tool that consumes them. Follow the tool's convention;
   do not rewrite them as `make-file.md` or `git-ignore.md` "for
   consistency".
3. **Project-imposed prefixes / suffixes.** Some projects add
   prefixes or suffixes that override generic slug rules — the
   tool/config manager, the language, or a code-style enforcement
   tool defines them. Examples vary widely by ecosystem (a build
   tool's `_test.go`, a framework's `module-info.java`,
   a code generator's `*.g.dart`). The rule is: when the project,
   its tooling, or its language ecosystem specifies a prefix or
   suffix, follow it. Document non-obvious project rules in
   `AGENTS.md`; this skill is not the right place for them.
4. **Kebab-case slugs (lowercase a–z + hyphens)** — only for files
   where *you* choose the name: notes, plans, design docs, how-to
   guides, knowledge-cache entries, rule files, skill subdirectories,
   etc.

The "Filename rules (universal)" section that follows applies inside
category (4). It must **not** override categories (1)–(3). When in
doubt, copy what the surrounding files in the repo already do; the
goal is to fit in with established conventions, not to apply a single
rule everywhere.

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

### ISO date prefix — knowledge-cache entries, notes, plans, postmortems

Pattern: `YYYY-MM-DD-<slug>.md`

- **Why ISO 8601:** sorts lexicographically; unambiguous across locales
  (Keep a Changelog §"Confusing Dates").
- **Where the date goes:** at the start of the filename, separated by
  `-`. The date *is* part of the filename, not the slug.
- **Same-day collisions:** append a counter, e.g.
  `2026-07-27-foo-2.md`. Avoid this by scanning `.tmp/docs/notes/`
  (or the cache) **and** running `kilo-shared-pull origin main` (the
  pre-create scan must surface cross-worktree collisions, not just
  local ones — see the `shared-context` skill).

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
| Postmortem | Sentence case, incident summary (`# 2026-08-10 GH Actions runbook flake`) |
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

.tmp/docs/notes/YYYY-MM-DD-<task-slug>.md
.tmp/docs/plans/YYYY-MM-DD-<task-slug>.md
.tmp/docs/postmortems/YYYY-MM-DD-<slug>.md
.tmp/docs/user_cache/<anything>            # git-tracked persistent user scratch
.tmp/scratch/<anything>                   # never commit
.tmp/migration/<anything>                  # never commit

.agents/docs/cache/README.md
.agents/docs/cache/<topic>/README.md
.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md

~/.config/kilo/rules/<slug>.md
~/.config/kilo/skills/<slug>/SKILL.md
~/.config/kilo/skills/<slug>/references/<slug>.md

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

Do not invent new stems (`NOTES.md`, `MEMOS.md`, etc.) when one of
the above will do.

## Project-specific prefixes and suffixes

Tool-specific prefixes and suffixes (a dotfile manager's `dot_*`,
a build system `_test.go`, a language's `_test.py`, a templating
engine's `*.tmpl`, a PEG-generated `*.peg`, etc.) override the generic
slug rules. **This skill is intentionally project-agnostic** — it
does not document those conventions. Document them in your project's
`AGENTS.md` and link to the relevant tool's documentation so future
agents can find them without re-deriving the rules.