# Knowledge Cache — Authoring Rules

These rules govern **how to write and use** knowledge-cache entries. For **where the cache lives in a project** (canonical placement, legacy path fallbacks, deviation policy), see the `project-layout` skill.

## Index

- Every cache directory must contain a `README.md` index.
- Before external research, read `<cache-dir>/README.md` to locate relevant entries and check their dates.
- If the cache directory or index is missing, **create** the directory and `README.md` before writing the first reusable entry, unless project rules prohibit the change. This is a precondition, not a question to ask first.
- List entries with relative links, topic, source, capture date, and a freshness or re-verification note. Keep the index concise. Do not duplicate entry contents.
- Update `README.md` whenever entries are added, changed, renamed, or removed.

## When to act on the cache

- If external research may be needed, locate the project cache and read its `README.md` during initial discovery.
- About to make a web lookup in this project → check the cache index first. If the index is missing or empty, create it and surface the cache convention in `AGENTS.md` → `Pointers` before spending web-tool credits.
- A cache hit is a prior fetch tagged with a date — re-verify if the domain is volatile (CLI tool or framework API released less than 6 months ago).
- Entry naming follows the canonical pattern from the `project-layout` skill: `<cache-dir>/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, with an ISO date prefix so the tree sorts chronologically.

## Git hygiene

The cache is **tracked** in this repo, so a fresh clone inherits the entries. Keep it that way unless the project decides otherwise. If the cache is transient, add the cache directory to `.gitignore` instead, and say so in the cache `README.md`.

## Reference

Authoritative tool-selection and cache-use guidance: `~/.agents/rules/web-verification.md` (loaded globally on every session). Canonical placement and naming: the `project-layout` skill.