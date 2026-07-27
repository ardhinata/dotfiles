# Pre-publish Checklists

Run the relevant checklist below before publishing any doc. Treat
**every** unchecked item as a blocker unless the doc type says
otherwise.

## Universal checklist (every doc)

- [ ] Filename follows `references/title-and-filename.md`
- [ ] One H1, matching (or near-matching) the filename slug
- [ ] Sections in the order required by the doc type
- [ ] Length under target; under hard ceiling
- [ ] All links resolve (no broken anchors, no 404s)
- [ ] All cross-repo links are relative paths, not absolute URLs
- [ ] All code blocks have a language identifier
- [ ] No secrets (tokens, keys, fingerprints, passwords)
- [ ] Frontmatter policy respected (see
      [`references/frontmatter.md`](../references/frontmatter.md))
- [ ] No speculation presented as fact (uncertain items are marked)

## Kilo rule file

- [ ] No frontmatter (project decision)
- [ ] Trigger / "When" header is unambiguous
- [ ] Rule body is concise (30–80 lines)
- [ ] Anti-patterns / exceptions noted if relevant
- [ ] "Captured sources" or "References" section if research-backed

## SKILL.md

- [ ] Frontmatter `name` matches parent dir name (lowercase, hyphens)
- [ ] Frontmatter `description` is third person, ≤ 1024 chars,
      names both *what* and *when*
- [ ] Body under 500 lines (push detail into references/)
- [ ] References are one level deep (no reference chains)
- [ ] All linked reference files exist
- [ ] `skills-ref validate ./<skill-dir>` passes (if available)

## Skill reference file

- [ ] Linked from `SKILL.md`
- [ ] Linked one level deep only (no chains)
- [ ] TOC present if file > 100 lines

## AGENTS.md

- [ ] Plain Markdown (no frontmatter)
- [ ] `Pointers` section references `README.md`
- [ ] 40–80 lines target; hard ceiling 150
- [ ] Every line answers "would an agent get this wrong without it?"
- [ ] `Boundaries` section uses 3-tier pattern if used
- [ ] No architecture overview or file tree

## README.md

- [ ] Plain Markdown (no frontmatter)
- [ ] Sections in Standard Readme order
- [ ] Short Description ≤ 120 chars, on its own line, no `>`
- [ ] Required sections present: Install, Usage, Contributing, License
- [ ] License full name + SPDX identifier
- [ ] `standard-readme-preset` passes (if available)

## Topic README.md

- [ ] Indexes every child file
- [ ] Plain Markdown
- [ ] < 100 lines

## Knowledge-cache entry

- [ ] Path: `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md`
- [ ] ISO date prefix matches today's date (or the date captured)
- [ ] Linked from the topic's `README.md`
- [ ] If new topic, topic `README.md` and root `README.md` updated
- [ ] Frontmatter `freshness` field set (or freshness note in body)
- [ ] `source` / `captured` fields or equivalent body sections

## Knowledge-cache topic / root README

- [ ] Every entry / topic file appears in the index table
- [ ] Each row has relative link + date + source
- [ ] Plain Markdown

## Transient note (.tmp/notes/)

- [ ] Filename matches `proactive-note-capture.md` rule
- [ ] Sections in the project's mandated order: Finding → Evidence →
      Why it matters → Scope → Uncertainty → Recommended destination →
      Date captured
- [ ] No secrets
- [ ] Pre-creation duplicate check performed
- [ ] `## Date captured` is ISO 8601

## Transient plan (.tmp/plans/)

- [ ] Filename matches `personal-quirks.md` rule
- [ ] Pre-planning duplicate scan done
- [ ] Sections: Goal, Scope, Steps, Current status, Risks
- [ ] Updated at every checkpoint (in place, not via new file)
- [ ] Length under 300 lines; split into phases if longer

## Persistent plan

- [ ] User-approved path
- [ ] Goal, Scope, Steps, Status sections
- [ ] Either committed (project rule says persistent plans may be
      committed) or in `.tmp/` per user direction

## ADR (MADR)

- [ ] Filename: `docs/adr/NNNN-<slug>.md`, NNNN 4-digit zero-padded
- [ ] Sections in MADR order
- [ ] At least one alternative considered beyond the chosen option
- [ ] Status field set (`proposed` / `accepted` / `rejected` / etc.)
- [ ] If superseded, successor ADR number referenced
- [ ] Decision date in frontmatter or section

## RFC

- [ ] Filename: `docs/rfcs/NNNN-<slug>.md`
- [ ] Reviewers listed in frontmatter
- [ ] Deadline set in frontmatter
- [ ] Summary at top, ≤ 1 paragraph
- [ ] Drawbacks section non-empty (don't hide costs)
- [ ] Open / unresolved questions explicit

## Design doc

- [ ] Goals AND non-goals stated (non-goals often missing)
- [ ] Each alternative gets a one-paragraph dismissal
- [ ] Proposed design walks through the user-visible change
- [ ] Links to related ADRs / RFCs

## CHANGELOG.md

- [ ] Plain Markdown
- [ ] Intro references Keep a Changelog and SemVer
- [ ] `[Unreleased]` section at top
- [ ] Latest version first
- [ ] Per-version ISO date `## [X.Y.Z] - YYYY-MM-DD`
- [ ] Sections within a version in this order: Added → Changed →
      Deprecated → Removed → Fixed → Security
- [ ] Yanked releases marked `[YANKED]`

## CONTRIBUTING.md

- [ ] Where to ask questions stated
- [ ] PR acceptance policy stated
- [ ] Code of Conduct linked (Contributor Covenant recommended)
- [ ] Any sign-off or formatting requirements explicit

## .tmp/scratch

- [ ] `.tmp/` is gitignored (project rule)
- [ ] Delete when done — no convention beyond that