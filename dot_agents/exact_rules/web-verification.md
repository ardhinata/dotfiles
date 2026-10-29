# Web Verification Policy

This file owns **when** to look something up and **what to do with the result**.

## Eager lookup policy

Use web tools proactively whenever the answer depends on current, external, or
specialized information. Do not rely on memory because a lookup feels
optional, and do not stop at a search snippet when the source can be opened.
Discover sources, read the relevant page, verify important claims, and cache
findings that are reusable on this machine.

## Startup rule

Read the project's local docs before any external research, then read the
project knowledge-cache `README.md` index. The canonical cache path is
`.agents/docs/cache/`. **If the cache directory or index is missing, create
it** as described by
`~/.agents/skills/project-context/references/knowledge-cache.md` — the index
is a precondition for writing the first entry, not something to ask about
first. Do not create it when project rules prohibit writes. Write a cache
entry only in a repository that already has `.agents/docs/cache/`. Otherwise
skip the cache and note the gap in your reply. `.tmp/` is for transient
scratchpads only — date-tagged web-learned facts go in `.agents/docs/cache/`,
not `.tmp/`.

## Escalation and verification

- If the first tool returns nothing useful, try the next form of the same
  lookup: a different query, a different tool, or the source URL directly.
- Verify consequential claims with a second tool.
- Prefer official documentation, primary sources, release notes, and source
  repos over blogs.
- Have a specific URL? Fetch it directly rather than searching for it.
- Have only a claim? Search for it. For multi-source synthesis across many
  pages, fan out to a subagent research role if the harness provides one.
- CLI tool or framework API released less than 6 months ago? Always
  re-verify with a fresh external lookup, even when the cache has an entry.

## Tool notes

`websearch` and `webfetch` are the web tools on this host. `websearch` takes
no per-call parameters. The `firecrawl_*`, `context7_*`, and `tavily_*` tools
do not exist here.

## Knowledge Staleness

Your training has a cutoff. When the gap to now is large relative to the
domain's volatility, prefer web tools even when you think you know the answer.

| Domain | Volatility | Verify when |
|---|---|---|
| CLI tool / package APIs | High (weeks–months) | Tool released less than 6 months ago |
| Framework / library APIs | Medium (months) | Cutoff → current is more than 3 months |
| Language specs / stable protocols | Low (years) | Cached knowledge is likely fine |
| Config formats / standards | Very low (decades) | Rarely needs verification |

For fast-moving domains, verify with a web tool before relying on cached
knowledge. When unsure, fetch rather than guess.

## Knowledge Caching

After any lookup that produces information reusable on this machine or likely
to go stale, write a date-tagged cache entry and update the index — placement
and authoring rules per the referenced skills. The cache is tracked in git, so
a fresh clone inherits the entries.
