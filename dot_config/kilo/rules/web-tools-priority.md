# Web Tool Priority

When performing web searches, scraping, or research, follow this priority order:

## Priority

1. **webfetch** (simple fetches) — free, zero billing. Use for straightforward content retrieval when you have a known URL and the page is simple (static HTML, blog posts, documentation). Built-in Kilo tool, not an MCP server.

2. **tavily** (primary search) — pay-as-you-go billed. Use for web searches where you don't know the exact URL. Returns 16+ results with reliable disambiguation, rich snippets, and broad source coverage. Benchmarked superior to firecrawl_search for ambiguous queries (e.g., correctly disambiguates "Next.js" vs clothing brand).

3. **firecrawl** (scraping and crawling) — free tier (limited credits). Use for scraping/crawling KNOWN URLs, not for search. Strengths: structured JSON extraction, screenshot, change tracking, monitoring, JavaScript-rendered pages. Use firecrawl_scrape when webfetch is truncated or the page needs JS rendering. Use firecrawl_crawl for multi-page extraction.

4. **context7** (library/API docs) — free. Use for library/API documentation lookups. Returns curated, in-page code snippets and structured API references. Benchmarked superior to firecrawl scrape for docs: 70% less token usage, zero page chrome, directly copy-pasteable code.

## Rationale

- `webfetch` is free; exhaust it first for known URLs
- `tavily` search quality (disambiguation, coverage, snippet richness) justifies pay-per-use for search
- `firecrawl` search is weak for ambiguous queries but excellent for scraping/crawling known URLs
- `context7` outperforms firecrawl scrape for documentation with curated code snippets and zero noise

## Knowledge Staleness: When to Prefer Web Tools

Your training knowledge has a cutoff date. When the gap between that cutoff and the present is large **relative to the volatility of the knowledge domain**, prefer web tools — even when you think you know the answer.

**Volatility heuristic** — estimate how fast the domain changes:

| Domain | Volatility | Example threshold |
|---|---|---|
| CLI tool / package APIs | **High** (weeks–months) | Skip cached knowledge for tools released < 6 months ago |
| Framework / library APIs | **Medium** (months) | Verify if cutoff → current > 3 months |
| Language specs / stable protocols | **Low** (years) | Cached knowledge is likely fine |
| Config formats / standards | **Very low** (decades) | Rarely need verification |

**Decision rule**: For fast-moving domains, verify with a web tool before relying on cached knowledge. When unsure, **err on the side of fetching**.

Examples:
- Asking about a CLI flag for a tool that released v2.0 last month → web search first
- Asking about Chezmoi v2.70+ features → verify against latest docs (`webfetch` or `context7`)
- Asking about git porcelain commands → cached knowledge is reliable
- Asking about Go 1.24 features released after your cutoff → `context7` or web search

## Knowledge Caching

After fetching up-to-date information from the web, **cache it in the project** so future sessions don't need to re-search. This reduces cost and latency.

**Where to cache**: Check the project's `AGENTS.md` (or equivalent context file) under its **Pointers** section — it should list the project's knowledge cache directories. Use those locations. If no cache location is defined, suggest creating one (a `.kilo/cache/` directory) and adding a pointer in `AGENTS.md`. See `project-context-setup.md` for conventions.

**What to cache**:
- Version-specific CLI changes, deprecated flags, new subcommands
- API breaking changes or new features not in your training data
- Configuration format updates
- Any fact you had to web-search for that is likely to be asked about again

**Format**: Keep entries concise. Use bullet points or short tables. Tag with the date fetched so future sessions can re-evaluate staleness. Example:

```markdown
<!-- In the project's knowledge cache directory (see AGENTS.md Pointers) -->
<!-- Tag each entry with the date it was fetched. -->
- **Chezmoi**: re-encrypt behavior changed in v2.70+; verify with webfetch before relying on cached syntax.
```

**When NOT to cache**:
- News, weather, stock prices, or other ephemeral data
- One-off answers unlikely to be needed again
- Content covered by NDA or proprietary restrictions

## Anti-Patterns

- Do not use `tavily` or `firecrawl` when `webfetch` can fetch the same URL directly
- Do not use `firecrawl_search` for ambiguous queries — use `tavily_search` instead
- Do not use `firecrawl_search` → `firecrawl_scrape` for documentation — use `context7` instead
- Do not use `context7` for general web searches or non-library queries
- Do not use `tavily` when you already have the exact URL to scrape
- Do not re-web-search for facts already cached in the project's knowledge cache directory (see `AGENTS.md` Pointers) unless the cached entry is stale
