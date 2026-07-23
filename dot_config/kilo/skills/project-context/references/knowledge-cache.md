# Knowledge Cache Convention

Use a per-project cache directory to store date-tagged web-learned facts so future sessions do not re-search the same answers.

Common cache locations (pick the project convention once and stick with it):

- `.tmp/doc-cache/` — transient, per-project
- `docs/cache/` — discoverable from `docs/`

Pick the directory whose style matches the rest of the project; if the project uses multiple, use the most transient.

## Cache index

- Every cache directory must contain a `README.md` index.
- Before external research, read `<cache-dir>/README.md` to locate relevant entries and check their dates.
- If the cache directory or index is missing, create the directory and `README.md` before writing the first reusable entry, unless project rules prohibit the change.
- List entries with relative links, topic, source, capture date, and a freshness or re-verification note. Keep the index concise; do not duplicate entry contents.
- Update `README.md` whenever entries are added, changed, renamed, or removed.

## When to act on the cache

- If external research may be needed, locate the project cache and read its `README.md` during initial discovery.
- About to call `tavily_*`, `firecrawl_*`, or `context7_*` for the first time in this project → check the cache index first; if missing or empty, create the index and surface the cache convention in `AGENTS.md` → `Pointers` before burning web-tool credits.
- A cache hit is a prior fetch tagged with a date — re-verify if the domain is volatile (CLI tool or framework API released less than 6 months ago).
- Entry naming: `<cache-dir>/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, with an ISO date prefix so the tree sorts chronologically.

If absent, suggest adding the cache directory and its `README.md` index to `.gitignore` when the cache is transient.

## Reference

Authoritative tool-selection and cache-use guidance: `~/.config/kilo/rules/web-tools-priority.md` (loaded globally on every session).