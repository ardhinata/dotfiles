# Web Tool Priority

Tool names below show short form → actual exposed name.

**Eager lookup policy:** Use web tools proactively whenever the answer depends on current, external, or specialized information. Do not rely on memory because a lookup feels optional, and do not stop at a search snippet when the source can be opened. Use the tools until the question is resolved: discover sources, read the relevant page, verify important claims, and cache reusable findings.

**Startup rule:** Before external research, skim the local `README.md` and `AGENTS.md`, then read the project knowledge-cache `README.md` index. The standard cache path is `.agents/docs/cache/`; legacy `.tmp/doc-cache/` and `.help/` are acceptable fallbacks. If the cache directory or index is missing, create the index as described by `~/.config/kilo/skills/project-context/references/knowledge-cache.md` before writing fetched facts, unless project rules prohibit writes. `.tmp/` is for transient scratchpads only — date-tagged web-learned facts go in `.agents/docs/cache/`, not `.tmp/`.

## Decision rule

1. **Have a URL?** → **`webfetch`** first; failed, truncated, or JS-required? → **`firecrawl_scrape`** with `waitFor: 5000`–`10000`.
2. **No URL, need discovery?** → **`websearch`** (free, broad coverage). Need finer filters (`time_range`, `include_domains`, `search_depth`)? → `tavily_search`. Need multi-source synthesis across many pages? → `tavily_research` (slow, $$). GitHub-only? → `firecrawl_search` with `categories: ["github"]`. Academic papers? → `firecrawl_research_search_papers` (arXiv-indexed) or `firecrawl_search` with `categories: ["research"]`. GitHub code/issue/implementation? → `firecrawl_research_search_github` (primary sources) or `firecrawl_developer_search` (developer-tuned index). Known commit hash or raw code? → `websearch` (often better than `firecrawl_developer_search` for direct commit hashes).
3. **Library/API question?** → `context7_resolve-library-id` → `context7_query-docs`. If 0 hits, fall back to `websearch`.
4. **Need to crawl a domain or fetch many pages?** → `tavily_crawl` / `tavily_map` (cheaper, plain HTML) or `firecrawl_crawl` / `firecrawl_map` (with JS rendering).
5. **Need structured extraction?** → `firecrawl_extract` (with JSON schema) or `tavily_extract` (plain extraction).

## Priority table

| Tier | Tool | Strong suit | Caveat |
|---|---|---|---|
| 1 | `webfetch` (built-in) | Known URL → markdown/HTML/text/JSON; free, no billing | Fails on JS-required pages; 404 on moved URLs (re-search to relocate) |
| **1.5** | **`websearch`** (built-in) | **URL discovery across general/niche/standards content; 2026-fresh; free, no MCP billing** | **No multi-source synthesis, no JS rendering, no library index, no domain filters** |
| 2 | `tavily_search` | Same as websearch + `time_range` / `include_domains` / `search_depth` filters | MCP billing; websearch is comparable on quality |
| 2 | `tavily_extract` | Extract content from a known URL | webfetch is free |
| 2 | `tavily_crawl` / `tavily_map` | Multi-page crawl with depth/breadth limits | websearch cannot do this |
| 2 | `tavily_research` | Multi-source synthesis across many pages (~280s, $$) | Highest cost; only for questions that need several perspectives |
| 3 | `firecrawl_scrape` | JS rendering, structured extraction, screenshots | Use after webfetch fails; billable |
| 3 | `firecrawl_crawl` / `firecrawl_map` | Multi-page crawl with JS rendering | websearch cannot do this |
| 3 | `firecrawl_search` | Web search with `categories` filter (`github` / `research` / `pdf` / `developer`) | MCP billing; websearch is comparable on quality |
| 3 | `firecrawl_extract` | Structured extraction with JSON schema | Use when you need specific fields, not just the page |
| 3 | `firecrawl_agent` | Async multi-source research | Overlaps with `tavily_research` |
| 3 | `firecrawl_parse` | Parse a known local/remote document (PDF/Word/etc.) into structured fields | Use when webfetch returns the page but not the right structure |
| 3 | `firecrawl_research_search_papers` | arXiv-indexed academic paper search; returns title + abstract for each hit | Requires OAuth/API key; empty pool for non-arXiv topics |
| 3 | `firecrawl_research_inspect_paper` | Per-paper metadata (authors, categories, dates, affiliation, abstract) given an arXiv/PMC/PMID/DOI ID | Requires OAuth/API key; do not pass raw URLs |
| 3 | `firecrawl_research_read_paper` | In-body paper passages ranked by a question (answers specific quantitative claims) | Requires OAuth/API key; full text only for indexed papers |
| 3 | `firecrawl_research_related_papers` | Citation graph walk from a seed paper (similar / citers / references) | Requires OAuth/API key; empty pool for fresh seeds (<6 months old) with no citations yet |
| 3 | `firecrawl_research_search_github` | GitHub-tuned search returning primary sources (code, issues, READMEs) | Requires OAuth/API key; matches `websearch` on quality for general queries, better for canonical repos |
| 3 | `firecrawl_developer_search` | Developer-tuned search (news + secondary sources) | Requires OAuth/API key; weaker than `websearch` for raw commit-hash queries |
| 4 | `context7_resolve-library-id` + `context7_query-docs` | **Indexed library docs with code snippets from the actual repo, version-locked** | Only works for libraries in context7's index (e.g., gpg-agent fails) |
| 4b | `websearch` (fallback) | When context7 fails to resolve the library | Already covered in tier 1.5 |

## Escalation and verification

- If the first tool returns nothing useful, escalate per the decision rule steps.
- Verify consequential claims with a second tool.
- Prefer official documentation, primary sources, release notes, and source repos over blogs.
- Have a specific URL? → `webfetch` to it first. Failed or incomplete? → `firecrawl_scrape` with `waitFor: 5000`–`10000`, then `firecrawl_map` for documentation sites whose content is elsewhere.
- Have only a claim? → `websearch` (or `tavily_search` when you need filters); use `tavily_research` when several sources or perspectives are needed. For a specific arXiv paper, the chain is `firecrawl_research_search_papers` → `firecrawl_research_inspect_paper` → `firecrawl_research_read_paper`. For related work, add `firecrawl_research_related_papers` (only when the seed is well-cited).
- Library/API question? → resolve with `context7_resolve-library-id`, then use `context7_query-docs`. If 0 hits, fall back to `websearch`.
- CLI tool or framework API released less than 6 months ago? → always re-verify with a fresh external lookup, even when the cache has an entry.

**Auth-gated firecrawl tools (require `kilo mcp auth firecrawl` or `FIRECRAWL_API_KEY` in env):** `firecrawl_developer_search`, `firecrawl_research_search_papers`, `firecrawl_research_inspect_paper`, `firecrawl_research_read_paper`, `firecrawl_research_related_papers`, `firecrawl_research_search_github`, `firecrawl_monitor_*`. After OAuth, all but `firecrawl_monitor_*` are usable in this env (verified 2026-08-17 in `.agents/docs/cache/kilo-webtools-benchmark/2026-08-17-kilo-webtools-benchmark.md` Round 3). Fall back to `websearch` / `tavily_search` with domain filters, `firecrawl_search` with `categories: ["github"]` / `["research"]`, or `tavily_research` if auth is unavailable.

## Knowledge Staleness

Your training has a cutoff. When the gap to now is large relative to the domain's volatility, prefer web tools even when you think you know the answer.

| Domain | Volatility | Verify when |
|---|---|---|
| CLI tool / package APIs | High (weeks–months) | Tool released less than 6 months ago |
| Framework / library APIs | Medium (months) | Cutoff → current is more than 3 months |
| Language specs / stable protocols | Low (years) | Cached knowledge is likely fine |
| Config formats / standards | Very low (decades) | Rarely needs verification |

For fast-moving domains, verify with a web tool before relying on cached knowledge. When unsure, fetch rather than guess.

## Knowledge Caching

After any lookup that produces reusable or volatile information, write a date-tagged entry under the project's knowledge-cache directory (`.agents/docs/cache/` preferred; legacy `.tmp/doc-cache/` is acceptable when `.agents/` is not yet established) and update that directory's `README.md` index with a relative link, topic, source, capture date, and freshness note. Do not cache ephemeral one-off answers or secrets. For canonical directory placement and entry naming see the `project-layout` skill; for cache-entry authoring rules (date tag, source, freshness note) see `~/.config/kilo/skills/project-context/references/knowledge-cache.md`.
