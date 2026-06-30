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

## Anti-Patterns

- Do not use `tavily` or `firecrawl` when `webfetch` can fetch the same URL directly
- Do not use `firecrawl_search` for ambiguous queries — use `tavily_search` instead
- Do not use `firecrawl_search` → `firecrawl_scrape` for documentation — use `context7` instead
- Do not use `context7` for general web searches or non-library queries
- Do not use `tavily` when you already have the exact URL to scrape
