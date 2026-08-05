# Anti-Patterns

Common mistakes when authoring documentation. Use this as a self-review
checklist before publishing any doc.

## Length anti-patterns

- **Bloat.** "Just one more section". Each addition must answer
  "would the reader miss this without it?". If no, cut.
- **Archival.** "We might need this someday". Capture in
  `.tmp/notes/` instead. Promote only when used.
- **Restating the rule.** Repeating the doc-type spec inside the
  doc. Cite, don't reproduce.
- **Massive code blocks.** 200+ lines of inline code should be a
  separate file with a link.
- **Markdown as prose.** Walls of paragraphs without headings, lists,
  or tables. Reformat to use structure.

## Structure anti-patterns

- **Multiple H1s.** Markdown allows it; renderers don't. One H1 per
  file.
- **Numbered headings.** `## 1. Findings`. The doc has a filename.
  Use the filename for numbering (MADR ADR-0002).
- **Skipping heading levels.** H2 → H4 without an H3 in between.
  Either re-level or restructure.
- **Inverted pyramid.** Putting the conclusion at the end. Put the
  point first; details after.
- **Decorative sections.** `## 🎉 Conclusion` or `## Some thoughts`.
  Use the doc's actual ending sections (`Status`, `References`,
  `Open questions`).

## Filename anti-patterns

- **Spaces or capitals in filenames.** `My Notes.md` is a disaster;
  use `my-notes.md`.
- **Underscores as separators.** `my_notes.md` is hard to type and
  inconsistent with the rest of the web. Use `my-notes.md`.
- **Non-ASCII filenames.** `café.md` may render fine but breaks
  shell, IDE find-in-files, and git hooks in unpredictable ways.
- **Date *inside* the slug.** `plan-2026-07-27-foo.md` makes the
  date part of the slug. The convention is `YYYY-MM-DD-foo.md` —
  date prefix, then slug.
- **Stale "v2", "v3" suffixes.** When the file is a rewrite, replace
  the old file or move it to an archive folder; do not version in the
  filename.

## Frontmatter anti-patterns

- **Frontmatter on a type that forbids it.** Kilo rule files in this
  repo do not use frontmatter (global decision). Do not copy
  `SKILL.md`'s frontmatter onto a rule file.
- **Required fields missing on a type that requires it.** `SKILL.md`
  without `name` or `description` fails `skills-ref validate`.
- **Trailing whitespace or BOM.** YAML parsers may reject files
  starting with a UTF-8 BOM. Save as plain UTF-8.
- **Reserved words as the `name` field.** `name: anthropic-helper`
  is invalid; "anthropic" is reserved per the agentskills.io spec.
- **Frontmatter as a comment.** Don't put notes to yourself in
  frontmatter; put them in the body.
- **Quotes inside frontmatter values.** `name: 'foo-bar'` is fine;
  `name: 'foo "bar"'` may need escaping. Prefer double quotes when
  the value contains single quotes or special characters.

## Content anti-patterns

- **Speculation framed as fact.** "This must be the case because…"
  without evidence is a finding, not a fact. Mark it as uncertain
  (see `proactive-note-capture.md`).
- **Duplication.** Two files describing the same thing. Either merge
  or link.
- **Stale content.** A "current state" doc that hasn't been touched
  in a year. Either re-verify or label "last verified YYYY-MM-DD".
- **Secrets in docs.** Tokens, private keys, fingerprints, recovery
  phrases — never. If a finding requires referencing one, point to
  the encrypted file and stop.
- **Outsourced content.** Long verbatim quotes from external sources.
  Cite and link; quote sparingly.
- **Marketing voice.** "blazingly fast", "next-gen", "the best".
  Strip adjectives; state the facts.
- **Vague timestamps.** "recently", "a while back", "next quarter".
  Use `YYYY-MM-DD` or "in v1.2.0".
- **Vendor-specific language in cross-vendor docs.** Don't write "if
  you're using Claude, do X" in a CHANGELOG or AGENTS.md.

## Linking anti-patterns

- **`click here`.** Replace with descriptive link text.
- **Absolute URLs for internal files.** Use relative paths.
- **Anchors that don't exist.** Broken anchors. Validate.
- **Three-deep relative paths.** Move the doc, not the link.
- **References to encrypted files by content.** Don't quote the
  content of `.age` / `.decrypted` / `encrypted_*` files even when
  linking.

## Process anti-patterns

- **Skipping the planning step.** Writing a doc without a plan when
  the doc is multi-section. Use the personal-quirks planning rule.
- **Skipping the duplicate check.** Not listing `.tmp/notes/` /
  `.tmp/plans/` before creating a new file. Causes drift.
- **Promoting a stale note.** A `.tmp/notes/` entry from a year ago
  probably no longer reflects current code. Re-verify before
  promoting to a durable doc.
- **Editing `AGENTS.md` without user review.** Project-context rule
  forbids unilateral edits; same for any project context file.
- **Editing the `web-tools-priority` cache without updating the
  topic README.** Forgetting the index entry makes the cache
  effectively invisible.

## Diátaxis-specific anti-patterns

- **Tutorials that explain.** If your tutorial has paragraphs of
  context, it is an explanation. Re-classify.
- **How-to guides that teach.** If your how-to includes "first,
  let's understand…", it is a tutorial. Re-classify.
- **Reference that instructs.** If your reference has numbered
  steps, it is a how-to. Re-classify.
- **Explanation that references the API.** If your explanation
  includes tables of fields, it is reference. Re-classify.
- **Mixing quadrants in one file.** A single doc serving one
  quadrant is clearer than one doc serving two.

## Markdown rendering anti-patterns

- **Hard-wrapped paragraphs.** Markdown doesn't need `\\` between
  lines; most renderers handle soft-wrap. Hard-wrap prevents
  reflow when the viewport changes.
- **Trailing two-space line breaks.** Use blank lines for
  paragraphs; the two-space hack is brittle.
- **Inline HTML for what Markdown can do.** Only use `<details>`,
  `<sub>`, `<sup>`, and similar when Markdown truly cannot express
  it.
- **Tabs in code blocks.** Spaces only. Tab width varies by reader.
- **Raw HTML links.** `[link](https://…)` not `<a href="…">link</a>`.
- **Plain text URLs.** Wrap URLs in `<…>` or ``[link](url)``. Bare
  URLs in prose confuse the parser and hurt accessibility.

## When you find an anti-pattern in your own draft

1. Identify which rule it violates. The reference files link back
   to the source spec.
2. Re-classify or re-cut, don't patch. Half-applied fixes are
   worse than the original.
3. If a pattern recurs, add it to this list with a one-line note
   about the trap.

## Source

This list synthesises findings from:

- Gloaguen et al., arXiv:2602.11988 — the
  context-file cost paper
- Diátaxis / Divio — quadrant confusion
- MADR — heading numbering, status field, YAML frontmatter
- Standard Readme — section order
- Keep a Changelog — `[Unreleased]`, date format, group ordering
- Global rules: `proactive-note-capture.md`,
  `personal-quirks.md`, `web-tools-priority.md`,
  `project-context.md`, `self-analysis.md`,
  `ambiguity-resolution.md`