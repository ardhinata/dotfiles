# Knowledge Cache Convention

Use a per-project cache dir to store date-tagged web-learned facts so future sessions don't re-search the same answers.

Common cache locations (pick the project convention once and stick with it):

- `.tmp/doc-cache/` — transient, per-project
- `.help/` — treats `chezmoi` and similar docs as supporting docs
- `docs/cache/` — discoverable from `docs/`

Pick the directory whose style matches the rest of the project; if the project uses multiple, use the most transient.

## When to act on the cache

- About to call `tavily_*`, `firecrawl_*`, or `context7_*` for the first time in this project → check the cache dir first; if missing or empty, surface that to the user and suggest a quick pointer add to `AGENTS.md` *before* burning web-tool credits.
- The cache hit is a prior fetch tagged with a date — re-verify if the domain is volatile (CLI tool / framework API released < 6 months ago).
- Entry naming: `cache/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, ISO date prefix so the tree sorts chronologically.

If absent, suggest creating the cache dir and adding it to `.gitignore`.

## Reference

Authoritative convention: `~/.config/kilo/rules/web-tools-priority.md` (loaded globally on every session).
