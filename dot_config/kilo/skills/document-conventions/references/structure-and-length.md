# Structure and Length Conventions

What sections each doc type needs, in what order, and how long the
whole thing should be. Use this together with
[`by-doc-type.md`](by-doc-type.md).

## Length philosophy

The single most common doc-conventions failure is **length drift**: the
file starts at 30 lines and ends at 300 because each reviewer added a
section "just in case". The cure is a target with a hard ceiling.

### Universal length heuristic

> **Target length = how much the agent can hold in working context while
> acting on the doc.** Hard ceiling = the point past which the doc must
> be split.

Concretely:

- Files under 100 lines → read whole, no ToC needed
- 100–300 lines → optional ToC if navigation helps
- 300–500 lines → required ToC; consider splitting
- 500+ lines → split into parent + references/

(Gloaguen et al., arXiv:2602.11988: even human-curated context files
raise inference cost > 20 %; LLM-generated ones measurably *reduce*
task success. Curate ruthlessly.)

### Per-type length budgets

| Type | Target | Hard ceiling | Why |
|---|---|---|---|
| Kilo rule file | 30–80 | 150 | Loaded every session; in shared context budget |
| SKILL.md | < 300 | 500 | Per agentskills.io — beyond 500, split into references/ |
| Skill reference file | as needed | 300 | Each is loaded on demand |
| AGENTS.md | 40–80 | 150 | Per project-context skill |
| README.md (project) | < 200 | 500 | Move detail to docs/ |
| Topic README.md | < 50 | 100 | Index, not content |
| Knowledge-cache entry | 30–150 | 300 | One finding per file |
| Knowledge-cache topic README | < 100 | 200 | Index, not content |
| Knowledge-cache root README | < 100 | 200 | Index, not content |
| Transient note | < 80 | 150 | Brief by design |
| Transient plan | < 150 | 300 | Update in place; if larger, split phases |
| Persistent plan | < 300 | 500 | Link out to design docs for depth |
| ADR (MADR) | 50–200 | 400 | One decision per ADR |
| RFC | 200–1000 | 2000 | Heavyweight; formal review |
| Design doc | 500–1500 | 3000 | Most flexible |
| CHANGELOG.md | unbounded | unbounded | Latest first; trim old versions per release |
| CONTRIBUTING.md | < 200 | 400 | Link out to detailed guides |
| .tmp/scratch | none | none | Delete when done |

## Section ordering

Some doc types have a **fixed** section order. Violating it breaks
tooling and reader expectation.

### Fixed order (must follow)

- **Standard Readme**: Title → Banner → Badges → Short Description →
  Long Description → ToC → Security → Background → Install → Usage →
  Extra → API → Maintainers → Thanks → Contributing → License
- **Keep a Changelog**: Title → Intro → `[Unreleased]` → `## [X.Y.Z] -
  YYYY-MM-DD` (latest first; within each version: Added → Changed →
  Deprecated → Removed → Fixed → Security)
- **MADR ADR**: Title → Context → Decision Drivers → Considered Options
  → Decision Outcome → Consequences → Confirmation → Pros/Cons of
  Options → More Info
- **Conventional Commits**: `<type>(<scope>)!: <description>` →
  optional body → optional footers (BREAKING CHANGE first)
- **Transient note** (global rule): Finding → Evidence → Why it
  matters → Scope → Uncertainty → Recommended destination → Date
  captured

### Loose order (recommended pattern)

For docs without a fixed spec, this order works well for agent-readable
Markdown:

1. **H1** (matching filename slug)
2. **One-line summary** (no heading; under the H1)
3. **`## When to load`** (skills, rules, references)
4. **`## Quick start`** or **`## TL;DR`** (long docs)
5. **`## Body`** — the actual content, broken into H2s
6. **`## Validation`** or **`## Testing`** (skills, rules, code)
7. **`## Anti-patterns`** or **`## Common mistakes`**
8. **`## References`** or **`## Sources`** — last

The principle: orient the reader (1–4), deliver the content (5),
enforce correctness (6–7), point to depth (8).

### Diátaxis-driven ordering

If the doc is end-user-facing, the ordering rules from
[Diátaxis](https://diataxis.fr/) apply:

- **Tutorial**: orientation → step 1 → step 2 → … → conclusion
- **How-to**: goal → prerequisites → steps → verification
- **Reference**: object/feature → description (alphabetical or code-ordered) → example
- **Explanation**: topic → why → context → opinions → alternatives

## Required vs. optional sections

A section is **required** if the doc type cannot fulfil its purpose
without it. Optional sections cover common cases but may be omitted.

### Universal required sections

Every doc needs:

- **An H1.** Equal to or near-equal to the filename slug.
- **A way to read it on its own.** No `previous.md` is a hard
  prerequisite for this file (relative links resolve on clone).

### Per-type required sections

| Type | Required sections |
|---|---|
| Kilo rule file | Trigger / "When" header; the rule body; (optional) Anti-patterns; References |
| SKILL.md | H1; body covering what + when; "When to load" if progressive disclosure |
| AGENTS.md | Pointers (cross-references to README.md + skills); recommended Boundaries (`✅ Always` / `⚠️ Ask first` / `🚫 Never`) |
| README.md | Title; Short Description (< 120 chars); Install; Usage; Contributing; License — per Standard Readme |
| Knowledge-cache entry | H1; Finding body; Source; Captured; Freshness note (if volatile) |
| Knowledge-cache topic README | Topic intro; Entries table |
| Knowledge-cache root README | Cache intro; Topics table |
| Transient note | Finding; Evidence; Why it matters; Scope; Uncertainty; Recommended destination; Date captured |
| Transient plan | Goal; Scope; Steps; Current status; Risks |
| Persistent plan | Goal; Scope; Steps; Status |
| ADR (MADR) | Title; Context and Problem Statement; Considered Options; Decision Outcome |
| RFC | Summary; Motivation; Detailed design; Drawbacks; Alternatives; Open questions |
| Design doc | Problem; Goals / non-goals; Proposed design; Alternatives considered |
| CHANGELOG.md | Title; intro referencing Keep a Changelog + SemVer; `[Unreleased]`; per-version sections |
| CONTRIBUTING.md | Where to ask; PR acceptance; CoC pointer |

## Section heading style

- **Sentence case for H2/H3**, except in ADR / RFC / Design Doc / README
  where Title Case is conventional (MADR: "ADR Template" headings are
  Title Case).
- **No trailing colons** on headings. `## Findings`, not
  `## Findings:`.
- **No numbering in headings.** (MADR ADR-0002). The filename carries
  any number.
- **Headings describe a section, not a sentence.** Prefer noun phrases
  over gerunds ("Captured sources" beats "Where this came from").
- **Heading levels are sequential.** Don't skip from H2 to H4.
- **No H1 in the body.** The H1 lives at the top.

## Inline structure rules

- **Lists for parallel items.** Two or more parallel points → bullets.
  Step-by-step → ordered list.
- **Code blocks for commands and snippets.** Always set the language
  identifier (` ```bash `, ` ```yaml `, ` ```python `). Omit only for
  plain text that should not be highlighted.
- **Tables for parameter docs and status matrices.** Markdown tables
  render well in every renderer.
- **Blockquotes for callouts.** `> Note: ...` for tips; `> ⚠️ Warning`
  for cautions.
- **Inline code for identifiers.** File names, function names, command
  names — wrap in backticks.

## Self-review: is this doc the right shape?

Before publishing, walk through this checklist. If you answer "no" to
more than one, re-cut:

1. Does the H1 match the filename slug?
2. Are required sections present?
3. Is the section order correct for the doc type?
4. Is the file under its length budget?
5. Does every section earn its place? (Cut anything that does not
   pass "would the reader miss this without it?".)
6. Are all links relative (within the repo) or absolute URLs
   (external)?
7. Does the file declare its source / capture date (if relevant)?