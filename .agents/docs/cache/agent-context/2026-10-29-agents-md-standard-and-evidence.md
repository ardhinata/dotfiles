# AGENTS.md — the Standard, the Evidence, the Corrections

Verified 2026-10-29 against the primary sources. Each row links to the page
it came from.

## The standard

- Steward: the [Agentic AI Foundation](https://aaif.io/projects/agents-md/),
  under the Linux Foundation. The formation was announced on 9 December 2025,
  with OpenAI's AGENTS.md as one of three founding contributions alongside
  MCP and goose.
- Canonical site: <https://agents.md/>. Source repository:
  <https://github.com/agentsmd/agents.md>.
- The site lists **23 agents** in its compatibility grid. It never states a
  count of its own, and it reports the format in use across more than 60,000
  open-source projects.
- The FAQ is an **on-page section** at <https://agents.md/#faq>. The path
  `https://agents.md/faq` returns 404.

### The "30+ agents" figure

It comes from a third-party blog, not the spec. ro14nd.de says "It already
works with 30+ agents". A mirror of the spec says "over 20". Archive
snapshots of agents.md from January 2025 to October 2026 never contain
"30+". Cite 23, or cite the site without a number.

### Claude Code

Reads `AGENTS.md` natively since **v2.1.277**:

> "Claude Code can read `AGENTS.md` as your project instructions, so a
> repository already set up for other coding agents works without adding a
> `CLAUDE.md`, an import, or a setting."

The `@AGENTS.md` import inside `CLAUDE.md` is the documented bridge when a
`CLAUDE.md` exists or a session cannot load `AGENTS.md`. It is no longer the
only way in.

### Copilot

GitHub Docs says "a single `CLAUDE.md` or `GEMINI.md` file", and the support
matrix lists "Agent instructions (using `AGENTS.md`, `CLAUDE.md` or
`GEMINI.md` files)". The word is **or**, not "alongside".

## The two studies

| | 2601.20404 (Lulla and others) | 2602.11988 (Gloaguen and others) |
|---|---|---|
| Question | Runtime and token cost | Task success rate |
| Agent | Codex only, gpt-5.2-codex | Four models, several agents |
| Context files | Root `AGENTS.md`, curated | Generated and developer-committed |
| Task success | Not measured | Measured. No significant gain |
| Cost | Output tokens down 16.58% median. Total tokens up 1.29% median | Inference cost up over 20% |
| Result | Faster and cheaper per output token | No success gain, at a cost |

They measure different things, so they do not strictly refute each other.

Lulla and others, arXiv:2601.20404v2: "the presence of AGENTS.md is
associated with a lower median runtime (Δ 28.64%) and reduced output token
consumption (Δ 16.58%), while maintaining a comparable task completion
behavior". Two limits the paper states: it does not measure task success
("A comprehensive evaluation of the output quality ... is beyond the scope of
this paper"), and the token result is mixed. Median **input** tokens rose
3.41% and median **total** tokens rose 1.29%.

Gloaguen and others, arXiv:2602.11988v3: "providing context files does not
generally improve task success rates, while increasing inference cost by over
20% on average". The detail that matters: generated files changed success by
-0.5% (p = 0.87) and -2% (p = 0.37), both insignificant. Developer-written
files beat generated ones by 7% (p = 0.038). Generated files helped by 2.7%
only when all other documentation was removed.

So the correct phrasing is "no significant effect on success", not "reduce
task success". And the developer-written advantage is the one significant
difference the paper found.

## Published size limits

| Vendor | Limit | Source |
|---|---|---|
| Cursor | "Keep rules under 500 lines" | [Cursor rules docs](https://cursor.com/docs/context/rules) |
| Claude Code | "target under 200 lines per CLAUDE.md file" | [Claude Code memory docs](https://code.claude.com/docs/en/memory) |
| Codex | `project_doc_max_bytes`, 32 KiB by default, combined across all loaded instruction files | [Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md/) |

## The MSR '26 survey

[Context Engineering for AI Agents in Open-Source Software](https://arxiv.org/abs/2510.21413),
MSR '26, Rio de Janeiro. 466 open-source projects. `AGENTS.md` files averaged
142 lines with a standard deviation of 231, and the survey found no settled
content structure. The file's high variation is the finding, not the mean.

## The Matt Nigh post

[How to write a great agents.md: Lessons from over 2,500 repositories](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-2500-repositories),
Matt Nigh, 19 November 2025. The author, the date and the sample size all
hold up.

Two caveats. The 2,500 files are GitHub Copilot **custom-agent personas** in
`.github/agents/`, with YAML frontmatter and a role persona. They are not
repository-root `AGENTS.md` context files. And the post reports "clear
boundaries" as a differentiator. The three-tier shape comes from the
author's example and starter template, not from a finding that 2,500 files
used three tiers.

## README scope

[GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
documents five items: what the project does, why it is useful, how users get
started, where users get help, who maintains and contributes.

The [jehna template](https://github.com/jehna/readme-best-practices) adds
licence and links, and its sections are Installing, Initial Configuration,
Developing, Building, Deploying, Features, Configuration, Contributing,
Links, Licensing.

Do not merge the two lists under one citation.

## Third-party sources that have gone stale

Two of the cited guides still say Claude Code cannot read `AGENTS.md`
natively. That stopped being true in v2.1.277:

- [ro14nd.de](https://ro14nd.de/what-goes-in-agents-md/)
- [Augment Code](https://www.augmentcode.com/guides/how-to-build-agents-md)

Augment Code also dates the ETH preprint to 23 June 2026, which is v2. The
current version is v3, 29 September 2026.

## Freshness

The standard moved fast in 2025 and 2026: the format shipped with Codex in
August 2025 and moved to the AAIF in December 2025. Claude Code's native
support landed in 2026. Re-verify the agent list and the vendor limits
before relying on them.
