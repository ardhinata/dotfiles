# Knowledge-Cache Topic README Template

Copy to `.agents/docs/cache/<topic>/README.md`. Lists every entry in
the topic. Plain Markdown — no frontmatter.

```markdown
# <Topic name>

<one-line description of what this topic covers>

## Entries

| Date | Slug | Source | Freshness | Notes |
|---|---|---|---|---|
| YYYY-MM-DD | [first-slug](./YYYY-MM-DD-first-slug.md) | <source> | stable | <one-line> |
| YYYY-MM-DD | [second-slug](./YYYY-MM-DD-second-slug.md) | <source> | check-2027-01 | <one-line> |

## How this topic is curated

<Optional: who adds entries, what counts as in-scope, how to verify.>

## Related topics

- [../other-topic/](../other-topic/README.md)
```

**Length:** < 100 lines.

**Rules:**

- Every entry file in this directory appears in the table
- Date column is ISO
- Source column is short (a domain is enough; link is in the entry)
- Freshness column matches the entry's `freshness` field

**Verification:** manual review against [`../checklists.md`](../checklists.md).