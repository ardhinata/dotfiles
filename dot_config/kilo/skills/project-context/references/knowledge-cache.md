# Knowledge Cache Convention

Use a per-project cache directory to store date-tagged web-learned facts so future sessions do not re-search the same answers.

## Standard path

**`.agents/docs/cache/`** is the standard project knowledge-cache location. It sits inside `.agents/` (the unified agent-only directory) so it is not confused with public `docs/`, and it is distinct from `.tmp/` (transient scratchpad).

Other acceptable locations and when to use them:

- **`.agents/docs/cache/`** — preferred; aligns with the standard project layout and the AGENTS.md → Pointers reference
- **`.tmp/doc-cache/`** — legacy; only when `.agents/` is not yet established in the project. Migrate to `.agents/docs/cache/` when convenient
- **`docs/cache/`** — discoverable from `docs/`; acceptable when the project prefers a non-`.agents/` location

Pick the path once and stick with it. Update `AGENTS.md` → `Pointers` to point at the chosen cache.

## What goes where

- `.agents/docs/cache/` — **persistent**, date-tagged, indexed web-learned facts. Should be referenced from `AGENTS.md`.
- `.agents/docs/` — non-cache agent-only documentation (fetched references, canonical notes that do not fit the cache mold).
- `.tmp/` — **transient** scratchpad documents, scripts, temp files. Distinct from the cache; not indexed, not referenced from `AGENTS.md`.

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

## Git hygiene

If the cache is transient (default), add the cache directory to `.gitignore`. If entries are intended to be shared across clones, keep them tracked but document that decision in the cache `README.md`.

## Reference

Authoritative tool-selection and cache-use guidance: `~/.config/kilo/rules/web-tools-priority.md` (loaded globally on every session).