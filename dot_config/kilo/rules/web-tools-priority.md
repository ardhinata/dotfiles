# Web Tool Priority

Tool names below show short form → actual exposed name.

**Eager lookup policy:** Use web tools proactively whenever the answer depends on current, external, or specialized information. Do not rely on memory because a lookup feels optional, and do not stop at a search snippet when the source can be opened. Use the tools until the question is resolved: discover sources, read the relevant page, verify important claims, and cache reusable findings.

**Startup rule:** Before external research, skim the local `README.md` and `AGENTS.md`, then read the project knowledge-cache `README.md` index. If the cache directory or index is missing, create the index as described by `dot_config/kilo/skills/project-context/references/knowledge-cache.md` before writing fetched facts, unless project rules prohibit writes.

**Decision rule:** *Have a URL?* → **webfetch** first; failed, truncated, paywalled, or JS-empty? → **firecrawl_scrape** with `waitFor`. *No URL?* → **tavily_search** to find one. *Library/API question?* → **context7** after resolving the library ID. For broad research, use **tavily_research** rather than relying on one search result.

## Priority

1. **webfetch** (built-in, free, zero billing) — `webfetch`. Fetches any known URL that returns readable content: HTML, markdown, JSON, plain text, READMEs, changelogs, release notes, RFCs, and simple docs. **Always try this first when you have a URL.** Re-read the returned page; do not treat a search snippet as evidence. **Not for:** URL discovery or pages that require browser rendering.

2. **tavily** (primary discovery and research) — tools prefixed `tavily_tavily_*` (`tavily_tavily_search`, `tavily_tavily_extract`, `tavily_tavily_research`, `tavily_tavily_crawl`, `tavily_tavily_map`). Use `tavily_search` when you do not know the URL, `tavily_research` for multi-source questions, and `tavily_extract` after finding a relevant URL. Search broadly enough to find an authoritative or primary source, then open it. **Not for:** a URL already known to be readable by `webfetch`.

3. **firecrawl** (scrape/crawl) — tools prefixed `firecrawl_firecrawl_*` (`firecrawl_firecrawl_scrape`, `firecrawl_firecrawl_crawl`, `firecrawl_firecrawl_map`, `firecrawl_firecrawl_extract`, `firecrawl_firecrawl_search`, `firecrawl_firecrawl_agent`). Use it for known URLs when `webfetch` fails or when structured extraction, screenshots, crawling, or JavaScript rendering is needed. Use `firecrawl_map` before escalating to `firecrawl_agent` when the correct page is unclear. Use `firecrawl_crawl` for multiple related pages. **Not for:** ambiguous open-ended discovery when Tavily is available.

4. **context7** (library/API docs) — tools prefixed `context7_*` (`context7_resolve-library-id`, `context7_query-docs`). Resolve the exact library ID first, then query focused API or version questions. Prefer it over general web search for library documentation, and re-query when the answer is version-sensitive. **Not for:** general web searches or non-library questions.

## Escalation and verification

- If the first result is incomplete, stale, or indirect, use the next suitable tool or a narrower query automatically; do not answer from an unverified snippet.
- Prefer official documentation, primary sources, release notes, and source repositories. Use multiple sources when the claim is consequential, disputed, or likely to change.
- Have a specific URL? → `webfetch` to it first. Failed or incomplete? → `firecrawl_scrape` with `waitFor: 5000`–`10000`, then `firecrawl_map` for documentation sites whose content is elsewhere.
- Have only a claim? → `tavily_search` with the claim as a phrase; use `tavily_research` when several sources or perspectives are needed.
- Library/API question? → resolve with `context7_resolve-library-id`, then use `context7_query-docs`; do not substitute memory for current API behavior.
- CLI tool or framework API released less than 6 months ago? → always re-verify with a fresh external lookup, even when the cache has an entry.

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

After any lookup that produces reusable or volatile information, write a date-tagged entry under the project's knowledge-cache directory and update that directory's `README.md` index with a relative link, topic, source, capture date, and freshness note. Do not cache ephemeral one-off answers or secrets. Follow `dot_config/kilo/skills/project-context/references/knowledge-cache.md` for directory selection and entry naming.
