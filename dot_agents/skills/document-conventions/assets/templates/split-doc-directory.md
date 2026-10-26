# Split Doc Directory Template

Copy to `<doc-path>/README.md` when a doc passed its hard ceiling and was
split into a directory. The directory name is the slug the single file
would have had. Plain Markdown — no frontmatter.

```markdown
# <Task summary in sentence case>

<one-line description of what this doc covers>

**Status: <status>.** <one line on where the work stands.>

## Index

| File | Contents |
|---|---|
| [01-<section-slug>.md](01-<section-slug>.md) | <one line: what this section holds> |
| [02-<section-slug>.md](02-<section-slug>.md) | <one line: what this section holds> |

## <Section name>

<The executive summary. A reader who stops here must still get the point,
the conclusion, and the status.>

## Related

- [<other-doc>](<relative-path>)
```

**Length:** < 150 lines for the index. The index is an entry point, not a
copy of the sections.

**Rules:**

- The directory holds `README.md` plus section files named `NN-<section-slug>.md`
- The number is reading order. 2-digit zero-padded, starting at `01`, no gaps
- Every section file appears in the index table with a one-line description
- The index carries the summary and the status, not only a link list
- Each section file has one H1 matching its slug and stands on its own
- Cross-links between sections and back to the index are relative

**When to split:** the doc passed the hard ceiling for its type. For one
long subject. When the content holds several subjects, write separate docs
and link to them instead.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
