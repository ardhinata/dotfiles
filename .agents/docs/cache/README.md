# Knowledge Cache

Date-tagged, reusable facts learned from web research in this project. Persistent across sessions; read this index first before calling `tavily_*`, `firecrawl_*`, or `context7_*` to avoid re-fetching the same answer.

## Convention

- **Path:** `.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, ISO date prefix sorts chronologically.
- **Index:** this file lists every entry with relative link, topic, source URL, capture date, and a freshness note.
- **Scope:** only persistent, reusable, volatile facts belong here. One-off answers, scratchpads, and transient work go in `.tmp/`.
- **Re-verify:** CLI tool / framework APIs are volatile — re-verify if the entry is more than 6 months old, or if the domain has had a major release.

## Entries

### agent-skills-ecosystem

- [2026-07-28 — skills.sh / agentskills.io vs Kilo](agent-skills-ecosystem/2026-07-28-skills-sh-vs-kilo-comparison.md) — open skills format spec; Kilo's local skills are already spec-compliant. Sources: skills.sh, agentskills.io, anthropics/skills, vercel-labs/skills.
- [2026-07-28 — `.kilocode/skills/` is legacy; `.kilo/skills/` is canonical](agent-skills-ecosystem/2026-07-28-kilo-skill-path-canonicalization.md) — `.kilocode/` still hosts modes + MCP, but skills/rules moved to `.kilo/`. `vercel-labs/skills` CLI agent-target table is stale on this point. Sources: kilo.ai docs, Kilo-Org/kilocode#7886, kilo.ai migration guide.

### pinentry

- [2026-08-08 — prior art for pinentry wrapper / manager](pinentry/2026-08-08-pinentry-wrapper-prior-art.md) — survey of similar tools (Paraphraser/set-gpg-pinentry-program, heathcliff26/pinentry-keyring, io41's pinentry-1password.sh, BMTLab's pinentry-fingerprint.sh) plus PINENTRY_USER_DATA per-call pattern; validates the pivot to an owned wrapper and surfaces 6 refinements (PINENTRY_USER_DATA as third precedence, --query direction, recovery docs, etc.). Sources: GitHub, gists, Arch/Gentoo wikis, U&L, SuperUser, openSUSE forums.

## Related

- `.help/` — legacy project knowledge cache (chezmoi + sprig docs, quirks, doc index). See `.help/README.md`.
- `~/.config/kilo/rules/web-tools-priority.md` — global web-tool selection and cache-use policy.
