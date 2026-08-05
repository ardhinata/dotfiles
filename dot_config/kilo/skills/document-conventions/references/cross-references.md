# Cross-Reference Conventions

How to link between docs, when to use which link form, and how to cite
files and lines.

## Link forms

Three link forms are valid; each has a place.

### Relative path — between docs in the same repo

```markdown
See [the README](../../README.md) for an overview.
See [the project-context skill](../../project-context/SKILL.md).
See [decision matrix](references/decision-matrix.md) for the quick view.
```

**Use when:** linking to another file in the same repository.

**Rules:**

- Always start with `./` or `../` (or a sibling path). Never use bare
  filenames for cross-folder links.
- Paths use forward slashes, even on Windows
  (agentskills.io runtime requirement).
- Include the file extension (`README.md`, not `README`).
- Anchor links within the same file use just the fragment
  (`[Background](#background)`).

### Absolute URL — for external sources

```markdown
[agentskills.io specification](https://agentskills.io/specification)
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
[Gloaguen et al., arXiv:2602.11988](https://arxiv.org/abs/2602.11988)
```

**Use when:** linking to a webpage, paper, RFC, or external spec.

**Rules:**

- Use the canonical URL (not a tracking redirect or short link).
- If citing a paper or RFC, include the identifier in the link text
  (so the reader knows the source even if the link breaks).
- For web sources, cite the **capture date** in the surrounding text
  if the content may change (see "Stale-link policy" below).

### File path with line number — for code citations

```markdown
The fix is in `dot_shell/helper/executable_shellx:506`.
```

Or, when the path needs to be a clickable link:

```markdown
[`executable_shellx:506`](../../../../dot_shell/helper/executable_shellx.tmpl#L506)
```

**Rules:**

- Use the **chezmoi source path** (the file the agent edits), not the
  rendered target. `dot_shell/helper/executable_shellx.tmpl` not
  `~/.shellx`.
- Cite the line number as `:N` after the path. Surround the citation
  in backticks.
- For a range, use `:N-M` or list both lines (`executable_shellx:506
  and :510`).
- **Do not paste the code** into the doc unless the snippet is itself
  the answer. Cite, don't reproduce.

## When to use which form

| Link target | Form |
|---|---|
| Same file, other heading | ``[Background](#background)`` |
| Sibling file in same folder | ``[plan.md](plan.md)`` |
| Doc in adjacent folder | ``[CHANGELOG.md](../CHANGELOG.md)`` |
| Doc deep in repo | `[the project-context skill](../../project-context/SKILL.md)` |
| Skill reference in same skill | ``[references/X.md](references/X.md)`` |
| Web spec / paper / blog | absolute URL |
| Code citation (chezmoi source) | `path:line` (not a clickable link) |
| Code citation (rendered target) | `~/.path:line` only when the agent cannot use the source path |

## Anchors

GitHub-style anchors:

- Lowercase the heading
- Replace spaces with hyphens
- Drop punctuation except hyphens
- Drop leading/trailing hyphens

Examples:

| Heading | Anchor |
|---|---|
| `## When to load` | `#when-to-load` |
| `## Filename rules` | `#filename-rules` |
| `## Quick start` | `#quick-start` |
| `## How to use this matrix` | `#how-to-use-this-matrix` |

GitHub adds `-N` for duplicates (`#when-to-load-1`, `#when-to-load-2`).
Most other renderers match. Use a different heading if you want a
stable anchor.

## Stale-link policy

The web rots. Different sources rot at different rates (see
`web-tools-priority.md` volatility table). When citing a web source:

1. **Capture date** — note when you wrote the link.
2. **Link text** — include enough identifier that the link text
   remains useful if the URL breaks (`[Keep a Changelog 1.1.0]`,
   not just `[Keep a Changelog]`).
3. **Freshness note** — for knowledge-cache entries, mark
   `freshness: volatile` or `freshness: check-2027-01` in the
   frontmatter.
4. **Re-verify** — when the user asks you to refresh a doc, scan for
   `<https://...>` and check each.

For the project, the rule is `.agents/docs/cache/<topic>/` entries
must declare capture date and freshness. This skill follows the same
convention in its `## Captured sources` section.

## Link text

Link text should describe the target, not "click here".

| Bad | Good |
|---|---|
| `click [here](https://keepachangelog.com/)` | `[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)` |
| ``see [this](references/by-doc-type.md)`` | `[per-type tables](references/by-doc-type.md)` |
| ``[docs](docs/README.md)`` | `[docs README](docs/README.md)` |

Link text should make sense out of context (a screen-reader user
tabbing through links hears only the link text).

## File-path mentions

When a path appears inline (not as a link), wrap it in backticks:

```markdown
The rule lives at `~/.config/kilo/rules/proactive-note-capture.md`.
```

Avoid bare paths in prose. Backticks tell the renderer "this is a
literal" and prevent accidental linkification.

## Disambiguating "the same doc"

If two docs in the repo have the same basename (e.g. `README.md` in
many folders), qualify the link text:

```markdown
[docs README](docs/README.md)
[knowledge-cache README](.agents/docs/cache/README.md)
```

If two skills exist with the same `SKILL.md` filename (which they all
do), reference the **directory** as the identifier:

```markdown
See [the project-context skill](../../project-context/SKILL.md).
See [the chezmoi skill](../../../../../.agents/kilo/skills/chezmoi/SKILL.md).
```

Never use a bare `[SKILL.md]()` link.

## Anti-patterns in linking

1. **Absolute URLs to internal files.**
   `https://github.com/me/repo/blob/main/docs/foo.md` — this breaks
   the moment the repo moves (or you're reading the chezmoi source).
   Use a relative path.
2. **Anchoring to auto-generated headings.** If a heading is the
   result of a plugin (`<!-- GENERATED -->`) the anchor may not be
   stable. Write the heading yourself.
3. **Linking to a 404 page.** Validate every link at least once.
4. **Three-deep relative paths.** If you find yourself writing
   `../../../foo.md`, the doc is in the wrong place. Move it.
5. **Linking from one transient file to another.** `.tmp/notes/` and
   `.tmp/plans/` are ephemeral. If two transient docs need to
   reference each other, copy the relevant content into both, or
   promote the shared content to a durable doc.

## Tooling

| Tool | Purpose |
|---|---|
| `markdown-link-check` | Lint links in Markdown files |
| `markdownlint` | Catch malformed links (missing brackets, missing target) |
| GitHub / GitLab | Render Markdown and resolve anchors automatically; preview before commit |
| `grep` / `ripgrep` | Find every place a doc is referenced when renaming or moving |