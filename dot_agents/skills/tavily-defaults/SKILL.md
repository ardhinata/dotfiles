---
name: tavily-defaults
description: Optimized default parameters for Tavily MCP tools (tavily_search, tavily_extract, tavily_crawl, tavily_map, tavily_research). Load before any tavily_* call to choose the right search_depth, extract_depth, model, and chunking — the remote MCP's DEFAULT_PARAMETERS header only applies to tavily_search, so per-tool defaults must be passed explicitly.
---

# Tavily MCP — Optimized Defaults

The Tavily remote MCP (`mcp.tavily.com/mcp`, server `3.4.5` / npm `tavily-mcp@0.2.22`) only applies `DEFAULT_PARAMETERS` to `tavily_search`. The other 4 tools (`extract`, `crawl`, `map`, `research`) ignore it — their handlers call `axios.post(url, params)` directly without merging defaults. Every per-tool default below must be passed explicitly per call.

**Source of truth:** official Tavily docs (https://docs.tavily.com/documentation/api-reference/endpoint/* + best-practices pages) verified 2026-08-17 + live cost probes on `tavily_search` and `tavily_extract`.

## Quick reference — defaults table

| Tool | Default | Why | Override when |
|---|---|---|---|
| `tavily_search` | `search_depth="basic"`, `max_results=8`, `topic="general"` | 1 credit, ~2s, reranked chunks | `advanced` (2 credits) for niche/recent/multi-facet queries |
| `tavily_extract` | `extract_depth="basic"`, `format="markdown"`, `query=<rerank intent>` + `chunks_per_source=3` | 1 credit per 5 URLs, prevents context explosion | `advanced` for tables/JS-rendered pages |
| `tavily_crawl` | `max_depth=1`, `max_breadth=20`, `limit=50`, `extract_depth="basic"`, `allow_external=true` | Cheap site exploration | `select_paths` + `select_domains` to focus; `instructions` doubles cost |
| `tavily_map` | `max_depth=1`, `limit=50`, `allow_external=true` | 1 credit per 10 pages | `allow_external=false` to stay on domain |
| `tavily_research` | `model="mini"`, `output_length="standard"` | 4–110 credits, 5 min max | `pro` for broad multi-topic synthesis (15–250 credits, 15 min max) |

## Per-tool guidance

### `tavily_search`

**Cost tiers** (verified live 2026-08-17 with `include_usage=true`):

| `search_depth` | Credits | ~Latency | Content type | Use case |
|---|---|---|---|---|
| `ultra-fast` | 1 | lowest | NLP summary | Real-time, latency-critical |
| `fast` | 1 | low | Reranked chunks | Quick targeted snippets |
| `basic` (default) | 1 | ~2s | Reranked chunks | General-purpose — **the right default** |
| `advanced` | 2 | ~3s | Reranked chunks | Niche, recent, multi-facet, longer queries |

**Verified probe (2026-08-17, query="Tavily search depth best practices"):**
- `basic`: 1 credit, 2.15s, top-score 0.839, 1163 chars content
- `advanced`: 2 credits, 2.88s, top-score 0.854, 2386 chars (2 chunks via `chunks_per_source=3`)

**Quality is rarely worth 2× the cost** for general queries. The 0.015 top-score delta and 2× content is negligible when the top URL is already authoritative. Reach for `advanced` when:
- The first `basic` pass returns low scores (<0.5) or irrelevant results
- The query is a niche topic, very recent (<1 month), or has multiple distinct facets
- The query is **specific** — contains named APIs, error messages, multi-token constraints, or product+feature+limitation framings (e.g. `"AWS API gateway websocket with lambda custom domain cannot do PostConnect"`). Even if `basic` scores look fine, `advanced` often surfaces the unique Q&A / blog / tutorial that matches the exact framing; `basic` clusters on the popular pages and misses them.
- You're following up on a previous `basic` search that missed

**Validated heuristic refinement:** don't gate on `basic`'s score alone. A `basic` pass with all top scores ≥0.7 can still miss the deeplinks that answer a specific question. Judge by query specificity — if the query names a specific API, error, or "X cannot do Y" pattern, prefer `advanced` directly.

**Other defaults:**
- `max_results: 8` — higher dilutes quality (Tavily docs warn). 5–10 is the sweet spot.
- `topic: "general"` — only `general` and `news` are exposed in the MCP (`finance` is API-only).
- `chunks_per_source: 3` — default is fine; only lower to 1 if results are too verbose.
- `include_raw_content: false` — turn on only when you need full page text (then prefer `tavily_extract` instead).
- `include_images: false` — costs nothing extra but bloats response unless needed.
- `country: <full country name>` — boosts local results; use for region-specific queries.
- `time_range: "month"|"week"|"day"` — for recency.
- `start_date` / `end_date` — for precise date filters; setting both implicitly clears `time_range` (Tavily source `index.js:543`).
- `exact_match: true` — only for due-diligence / specific entity / quoted-phrase queries; narrows retrieval.
- `auto_parameters: true` — let Tavily auto-tune, but it may bump to `advanced` (2 credits). Avoid unless exploring; set `search_depth` explicitly to control cost.

### `tavily_extract`

**Cost:** 1 credit per 5 successful URLs (basic) / 2 credits per 5 URLs (advanced). Failed extractions are free.

**Verified probe (2026-08-17, single URL, `extract_depth=basic`):** 0 credits (below 5-URL threshold), 0.01s responded, 18838 chars returned.

**Always pair `query` with `chunks_per_source` to prevent context explosion:**

```json
{
  "urls": ["https://example.com/long-doc"],
  "query": "machine learning accuracy on benchmark X",
  "chunks_per_source": 3,
  "extract_depth": "basic"
}
```

Without `query`, you get the full page markdown — fine for short pages, dangerous for long ones.

**Use `extract_depth=advanced` only for:**
- JavaScript-rendered pages
- Tables and structured data
- Embedded media
- Higher extraction success rates (better at protected sites)

For LinkedIn-style sites or pages with heavy client-side rendering, `advanced` is the only option.

### `tavily_crawl`

**Cost:** `Mapping cost + Extraction cost`. 10 pages basic = 1 + 2 = 3 credits. 10 pages advanced = 1 + 4 = 5 credits. `instructions` doubles the mapping cost (1→2 credits per 10 pages).

**Defaults:** `max_depth=1`, `max_breadth=20`, `limit=50`, `extract_depth="basic"`, `format="markdown"`.

**Tighten scope with:**
- `select_paths: ["/docs/.*"]` — restrict to URL patterns
- `select_domains: ["^docs\\.example\\.com$"]` — restrict to subdomains
- `exclude_paths: ["/private/.*"]` — exclude paths
- `allow_external: false` — block off-domain links

**Avoid `instructions` unless worth the 2× mapping cost** — combines natural-language guidance with extraction. Equivalents: scope tightly with `select_paths` + `select_domains` + `limit`.

### `tavily_map`

**Cost:** 1 credit per 10 pages (no `instructions`) / 2 credits per 10 pages (with `instructions`).

Defaults match `crawl`. Use when you need URL inventory first, then extract selectively.

### `tavily_research`

**Cost boundaries** (per docs, 2026-08-17):

| Model | Min credits | Max credits | Max duration |
|---|---|---|---|
| `mini` (default here) | 4 | 110 | 5 min |
| `pro` | 15 | 250 | 15 min |
| `auto` (server default) | server picks | server picks | up to 15 min |

**Use `model="mini"`** for narrow, well-scoped questions. **Use `pro`** when the question explicitly spans multiple subtopics or domains. **Use `auto`** only when breadth is unknown.

**Other parameters:**
- `output_length: "short" | "standard" (default) | "long"` — typed control over response size (advisory, not a hard cap).
- `output_schema: {properties: {...}}` — JSON Schema for structured output. Must include `properties`, optionally `required`.
- `citation_format: "numbered" (default) | "mla" | "apa" | "chicago"`.
- `include_domains: [...20]` — soft preference (other domains can still appear).
- `exclude_domains: [...20]` — hard blocklist (subdomain matching is downward only).
- `files: [{name, data (base64), type: "base64"}]` — attach up to 5 files (.txt/.md/.json), max 80k words each.
- `stream: true` — SSE stream. Not supported in the MCP wrapper (which polls the result).

## The two-step pattern (search → extract)

Per Tavily's best-practices docs, the optimal workflow:

1. **Search** with `search_depth="basic"` to discover URLs
2. **Filter** by `score > 0.5` (or by domain / content)
3. **Extract** from top-ranked URLs with `query` + `chunks_per_source` + `extract_depth="basic"`

This is cheaper than `include_raw_content=true` in search (which extracts from every result) and avoids context explosion.

**End-to-end cost example (validated 2026-08-17, niche query):**
- `tavily_search` `search_depth="advanced"` (specific query) → 2 credits
- `tavily_extract` 2 URLs with `query` + `chunks_per_source=3` → 0 credits (below 5-URL threshold)
- **Total: 2 credits** for a complete search-to-answer pipeline.

If the first `basic` search is conclusive, skip `advanced` and save 1 credit. If the query is specific (named API, error, "X cannot do Y"), go directly to `advanced`.

## Defaults that **don't** work via `DEFAULT_PARAMETERS`

Only `tavily_search` honors `DEFAULT_PARAMETERS`. For other tools, set per call:

```jsonc
"DEFAULT_PARAMETERS": "{\"search_depth\": \"basic\", \"max_results\": 8, \"topic\": \"general\"}"
```

Setting `model: "mini"` here is a **no-op** for `tavily_research` — pass it explicitly per call.

## ⚠️ Critical: defaults **override** per-call args

The merge logic at `tavily-mcp@0.2.22` `index.js:534-539` is:

```js
for (const key in searchParams) {
    if (key in defaults) {
        searchParams[key] = defaults[key];   // ← defaults win
    }
}
```

This is the opposite of what most users expect. A key in `DEFAULT_PARAMETERS` is **forced**, not defaulted. If `kilo.jsonc` has `"search_depth": "basic"` in `DEFAULT_PARAMETERS`, **every** `tavily_search` call uses `basic` — even when the agent passes `search_depth: "advanced"` explicitly.

**Verified empirically (2026-08-17):** on the remote MCP (`mcp.tavily.com/mcp` v3.4.5), with `DEFAULT_PARAMETERS: {"search_depth": "advanced"}` and per-call `search_depth: "basic"`, response latency was 1.52s — clearly basic, not advanced (~3.3s). The remote MCP honors the same merge order as the local source.

**Rule of thumb:** if you want a per-call override to work, **don't** put that key in `DEFAULT_PARAMETERS`. The header is a "force" mechanism, not a "default that can be overridden".

**Recommendation for `kilo.jsonc`:** keep `DEFAULT_PARAMETERS` minimal. Only set values that are universally desired (e.g., `topic: "general"`). Avoid `search_depth` and `max_results` here — set them in the skill's per-call rule so the agent can override.

## Anti-patterns

- `search_depth="advanced"` for general lookups — 2× cost, marginal quality gain.
- `extract_depth="advanced"` by default — use only when the simpler depth fails (tables, JS).
- `include_raw_content=true` on search — bloats response; use `tavily_extract` with `query` instead.
- `tavily_research` without `model` — server defaults to `auto`; may pick `pro` (15–250 credits).
- `tavily_extract` without `query` on long pages — returns full page content, blows context.
- `auto_parameters=true` with explicit `search_depth` — auto may override to `advanced` silently.
- `max_results=20` — quality drops past ~10 (Tavily docs warn).
- `allow_external=true` on crawl/map when you only want the starting domain.
- `instructions` on crawl/map when scope can be tightened with `select_paths`/`select_domains` — costs 2× as much.

## Rate limits

Per `tavily-mcp` source (`index.js:585`), `tavily_research` has a hard-coded **20 requests/minute** rate limit. `tavily_search`/`extract` follow the plan's RPM. When batching, cap concurrency at `RPM/60 × avg_latency_s` (Tavily best-practices).
