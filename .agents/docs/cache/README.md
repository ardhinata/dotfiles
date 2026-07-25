# Knowledge Cache

Date-tagged, reusable facts learned from web research in this project. Persistent across sessions; read this index first before calling `tavily_*`, `firecrawl_*`, or `context7_*` to avoid re-fetching the same answer.

## Convention

- **Path:** `.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, ISO date prefix sorts chronologically.
- **Index:** this file lists every entry with relative link, topic, source URL, capture date, and a freshness note.
- **Scope:** only persistent, reusable, volatile facts belong here. One-off answers, scratchpads, and transient work go in `.tmp/`.
- **Re-verify:** CLI tool / framework APIs are volatile — re-verify if the entry is more than 6 months old, or if the domain has had a major release.

## Entries

_No entries yet. Add the first one when external research produces a reusable fact._

## Related

- `.help/` — legacy project knowledge cache (chezmoi + sprig docs, quirks, doc index). See `.help/README.md`.
- `~/.config/kilo/rules/web-tools-priority.md` — global web-tool selection and cache-use policy.
