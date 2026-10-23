# Web Verification Policy

Harness-neutral policy for external lookups. The *tools* differ per harness —
see the harness's own tool-routing rule for which tool to call. This file owns
**when** to look something up and **what to do with the result**.

## Eager lookup policy

Use web tools proactively whenever the answer depends on current, external, or
specialized information. Do not rely on memory because a lookup feels optional,
and do not stop at a search snippet when the source can be opened. Use the
tools until the question is resolved: discover sources, read the relevant page,
verify important claims, and cache reusable findings.

## Startup rule

Apply `local-first.md` before any external research, then read the project
knowledge-cache `README.md` index. The standard cache path is
`.agents/docs/cache/`; legacy `.tmp/doc-cache/` and `.help/` are acceptable
fallbacks. If the cache directory or index is missing, create the index as
described by `~/.agents/skills/project-context/references/knowledge-cache.md`
before writing fetched facts, unless project rules prohibit writes. `.tmp/` is
for transient scratchpads only — date-tagged web-learned facts go in
`.agents/docs/cache/`, not `.tmp/`.

## Escalation and verification

- If the first tool returns nothing useful, escalate to the next tier of the
  harness's tool-routing rule.
- Verify consequential claims with a second tool.
- Prefer official documentation, primary sources, release notes, and source
  repos over blogs.
- Have a specific URL? Fetch it directly rather than searching for it.
- Have only a claim? Search for it; for multi-source synthesis across many
  pages, fan out to a subagent research role if the harness provides one.
- CLI tool or framework API released less than 6 months ago? Always re-verify
  with a fresh external lookup, even when the cache has an entry.

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

After any lookup that produces reusable or volatile information, write a
date-tagged cache entry and update the index — placement and authoring rules
per the referenced skills.
