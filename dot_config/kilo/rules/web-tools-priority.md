# Web Tool Priority

Follow this priority for web search, scrape, and research. Tool names below show short form → actual exposed name.

## Priority

1. **webfetch** (built-in, free) — `webfetch`. Simple fetches of a known URL (static HTML, blog posts, docs). Exhaust this first; zero billing.

2. **tavily** (primary search) — tools prefixed `talivy_tavily_*` (`talivy_tavily_search`, `talivy_tavily_extract`, `talivy_tavily_research`, `talivy_tavily_crawl`, `talivy_tavily_map`). Pay-as-you-go. Use for web searches where you don't know the exact URL. Better disambiguation and snippet richness than firecrawl search (e.g. correctly separates "Next.js" from the clothing brand).

3. **firecrawl** (scrape/crawl) — tools prefixed `firecrawl_firecrawl_*` (`firecrawl_firecrawl_scrape`, `firecrawl_firecrawl_crawl`, `firecrawl_firecrawl_map`, `firecrawl_firecrawl_extract`, `firecrawl_firecrawl_search`). Free tier (limited credits). Use for **known URLs**, not search. Strengths: structured JSON extraction, screenshots, change tracking, monitoring, JS-rendered pages. Use `firecrawl_scrape` when `webfetch` is truncated or the page needs JS rendering; `firecrawl_crawl` for multi-page extraction.

4. **context7** (library/API docs) — tools prefixed `context7_*` (`context7_resolve-library-id`, `context7_query-docs`). Free. Library/API documentation lookups. Curated in-page snippets, structured API refs. ~70% less token usage and zero page chrome vs firecrawl scrape for docs.

## Anti-Patterns

- Do not use `tavily` or `firecrawl` when `webfetch` can fetch the same URL directly
- Do not use `firecrawl_search` for ambiguous queries — use `tavily_search`
- Do not chain `firecrawl_search` → `firecrawl_scrape` for documentation — use `context7`
- Do not use `context7` for general web searches or non-library queries
- Do not use `tavily` when you already have the exact URL to scrape

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

After fetching up-to-date info, **cache it in the project** so future sessions don't re-search.

- **Where**: the project's `AGENTS.md` **Pointers** section lists its knowledge-cache dirs (common: `.kilo/cache/`, `.help/`). If none is defined, suggest creating `.kilo/cache/` and adding a pointer. See `project-context-setup.md`.
- **What**: version-specific CLI changes, deprecated flags, API breaking changes, config-format updates — anything you had to web-search that may be asked again.
- **Format**: concise bullets or short tables, tagged with the date fetched.
- **When NOT to cache**: ephemeral data (news, prices), one-off answers, NDA/proprietary content.
