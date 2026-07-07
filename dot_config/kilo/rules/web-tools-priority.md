# Web Tool Priority

Tool names below show short form → actual exposed name.

**Decision rule:** *Have a URL?* → **webfetch** first; failed / truncated / JS-empty? → **firecrawl_scrape** with `waitFor`. *No URL?* → **tavily_search** to find one. *Library/API question?* → **context7**.

## Priority

1. **webfetch** (built-in, free, zero billing) — `webfetch`. Fetches any known URL that returns readable content: HTML, markdown, JSON, plain text, READMEs, changelogs, release notes, RFCs, simple docs. Failure modes: JS-rendered SPAs, very long pages (truncation), paywalled content. **Always try this first when you have a URL.** **Not for:** URL discovery (use tavily).

2. **tavily** (primary search) — tools prefixed `talivy_tavily_*` (`talivy_tavily_search`, `talivy_tavily_extract`, `talivy_tavily_research`, `talivy_tavily_crawl`, `talivy_tavily_map`). Pay-as-you-go. Use for web searches where you don't know the exact URL. Better disambiguation and snippet richness than firecrawl search (e.g. correctly separates "Next.js" from the clothing brand). **Not for:** known URLs (use webfetch or firecrawl_scrape).

3. **firecrawl** (scrape/crawl) — tools prefixed `firecrawl_firecrawl_*` (`firecrawl_firecrawl_scrape`, `firecrawl_firecrawl_crawl`, `firecrawl_firecrawl_map`, `firecrawl_firecrawl_extract`, `firecrawl_firecrawl_search`). Free tier (limited credits). Use for **known URLs**, not search. Strengths: structured JSON extraction, screenshots, change tracking, monitoring, JS-rendered pages. Use `firecrawl_scrape` when `webfetch` is truncated or the page needs JS rendering; `firecrawl_crawl` for multi-page extraction. **Not for:** ambiguous queries (use tavily_search); API docs (use context7).

4. **context7** (library/API docs) — tools prefixed `context7_*` (`context7_resolve-library-id`, `context7_query-docs`). Free. Library/API documentation lookups. Curated in-page snippets, structured API refs. ~70% less token usage and zero page chrome vs firecrawl scrape for docs. **Not for:** general web searches or non-library queries.

## Verification

Use the **cheapest tool that can answer**:

- Have a specific URL? → `webfetch` to it. Re-read the page; do not trust the snippet.
- Have only a claim? → `tavily_search` with the claim as a phrase. Prefer recency-tagged queries.
- Library/API question? → `context7` (no need to search the public web).
- CLI tool / framework API released < 6 months ago? → always re-verify; never rely on cached knowledge without a fresh fetch.

## Knowledge Staleness

Your training has a cutoff. When the gap to now is large **relative to the domain's volatility**, prefer web tools — even when you think you know the answer.

| Domain | Volatility | Verify when |
|---|---|---|
| CLI tool / package APIs | High (weeks–months) | Tool released < 6 months ago |
| Framework / library APIs | Medium (months) | Cutoff → current > 3 months |
| Language specs / stable protocols | Low (years) | Cached knowledge is likely fine |
| Config formats / standards | Very low (decades) | Rarely needs verification |

Decision rule: for fast-moving domains, verify with a web tool before relying on cached knowledge. When unsure, **err on the side of fetching**.

## Knowledge Caching

After fetching up-to-date info, **cache it in the project** so future sessions don't re-search. Conventions (location, format, when not to cache) live in the `project-context-setup` skill — load it before setting up a cache for the first time. The TL;DR: cache volatile-but-reusable facts (CLI/API changes, deprecations) under the project's knowledge-cache dir (common: `.tmp/doc-cache/`, `.help/`), one topic per file, ISO-date prefixed; do not cache ephemeral data, one-off answers, or secrets.
