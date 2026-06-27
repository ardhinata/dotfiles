# Web Tool Priority

When performing web searches, scraping, or research, follow this priority order:

## Priority

1. **webfetch** (simple fetches) — free, zero billing. Use for straightforward content retrieval when you have a known URL and the page is simple (static HTML, blog posts, documentation). This is a built-in Kilo tool, not an MCP server.
2. **firecrawl** (primary web tool) — flat-rate billing, high quality. Use when webfetch returns unusable output (truncated, missing content, JavaScript-rendered pages), or when you need advanced features: search across multiple sites, crawl, structured JSON extraction, change tracking, or monitoring.
3. **tavily** (fallback only) — pay-as-you-go billed. Use only when both webfetch and firecrawl are exhausted, return insufficient results, or you need tavily-specific capabilities (e.g., `tavily_search` with domain filtering, time range, or news/images sources that firecrawl misses).
4. **context7** — use only for library/API documentation lookups that firecrawl search + scrape cannot resolve. Context7 is documentation-specific, not a general search tool.

## Rationale

- `webfetch` is free with no usage limits; exhaust it first for simple fetches
- `firecrawl` is flat-rate, so it should carry the primary workload for complex tasks
- `tavily` is usage-billed; minimize unnecessary consumption
- `context7` is domain-specific (docs only); firecrawl can often achieve the same result with search + scrape

## Anti-Patterns

- Do not use `firecrawl` or `tavily` when `webfetch` can fetch the same URL directly
- Do not reach for `tavily` when `firecrawl` can handle the same query
- Do not use `context7` for general web searches
