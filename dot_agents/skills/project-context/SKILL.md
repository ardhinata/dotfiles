---
name: project-context
description: Use when starting work in a project that lacks `AGENTS.md`, when discovering non-obvious project conventions an AGENTS.md would eliminate, when a vendor-specific directory (`.cursor/`, `.claude/`, `.opencode/`, etc.) is found at the project root, or when integrating agent rules and skills under `.agents/<vendor>/`. Treats `AGENTS.md` as the canonical agent instruction standard — vendor files (CLAUDE.md, .cursorrules, .windsurfrules, GEMINI.md) stay one-line pointers to it, never a second source of truth. For project directory layout, `.tmp/` subroles, vendor path unification, and knowledge-cache placement, load the `project-layout` skill instead.
---

# Project Context

When starting work in a project, assess its agent-context and documentation state. When the project lacks agent-context, a standardized documentation layout, or a knowledge cache, **create** the missing pieces. The knowledge-cache directory and its `README.md` index are preconditions for writing cache entries, so do not ask about them first. Also suggest — do not auto-write — an `AGENTS.md`, which needs the user's review.

## Standard directory layout

For the canonical on-disk layout of an agentic-driven project (`AGENTS.md`, `README.md`, `docs/`, `.agents/`, `.agents/docs/cache/`, `.tmp/{scratch,migration}/`, vendor unification), **load the `project-layout` skill**. This skill owns the AGENTS.md lifecycle and README↔AGENTS separation. The layout itself is a single source of truth in `project-layout`.

## Proactive caching default

After any web lookup that produces reusable or volatile information, write a date-tagged entry under the project's knowledge cache. Update its `README.md` index. See the `project-layout` skill for canonical placement and naming. Prefer verified web sources over training-data recall. This is a global default, not a per-project `AGENTS.md` directive.

## AGENTS.md as the canonical standard

`AGENTS.md` is the open format stewarded by the [Agentic AI Foundation](https://aaif.io/projects/agents-md/) under the Linux Foundation (Dec 2025). The [agents.md site](https://agents.md/) lists 23 agents that read it, including Codex, Cursor, Copilot, Aider, opencode, Zed, Warp and Claude Code. The site also reports the format in use across more than 60,000 open-source projects. **Treat `AGENTS.md` as the canonical agent instruction standard.**

Claude Code reads `AGENTS.md` natively since v2.1.277. When a `CLAUDE.md` exists next to it, or a session cannot load `AGENTS.md`, the documented bridge is an `@AGENTS.md` import inside `CLAUDE.md`.

Do not *duplicate* guidance into `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules`, or `GEMINI.md`. Those files are vendor-owned, and several tools still read them. Copilot reads `CLAUDE.md` or `GEMINI.md` as an alternative to `AGENTS.md`, so a stale copy there still reaches the agent. When one exists, point it at `AGENTS.md` via an import (`@AGENTS.md`) so one canonical file drives every tool. New work goes in `AGENTS.md`. Vendor-specific overrides belong in `.agents/<vendor>/`.

Note: OpenCode does not expand `@file` references inside `AGENTS.md`. Use the `instructions` array in `opencode.json` for that, or tell the agent in `AGENTS.md` to read the referenced file on demand.

## Standard vs house style

**Backed by a published standard or convention:**

| Rule | Source |
|---|---|
| `AGENTS.md` as the cross-tool instruction file | agents.md (AAIF, Linux Foundation) |
| Nested `AGENTS.md`, closest-to-the-file wins | [agents.md FAQ section](https://agents.md/#faq), [Codex discovery order](https://developers.openai.com/codex/guides/agents-md/) |
| `README.md` for humans, `AGENTS.md` for agents | agents.md spec |
| 3-tier Boundaries (`Always` / `Ask first` / `Never`) | GitHub analysis of 2,500+ Copilot custom-agent files (Matt Nigh, Nov 2025) |
| Context files raise inference cost without reliably improving task success | Gloaguen and others, arXiv:2602.11988 |
| AGENTS.md cuts agent runtime and output tokens at equal task completion | Lulla and others, arXiv:2601.20404 |

The two studies measure different things, so they do not conflict. Lulla and others measured efficiency for Codex: curated `AGENTS.md` cut the median runtime by 28.64% and the output tokens by 16.58%. They did not measure task success at all. Gloaguen and others measured task success and cost across four agents: the files produced no significant gain, and they raised inference cost by over 20%. Developer-written files beat generated ones by 7%. A context file can make an agent faster without making it more correct.

The Matt Nigh analysis covered Copilot custom-agent personas in `.github/agents/`, not repository-root `AGENTS.md` context files. The transfer to a root `AGENTS.md` is reasonable, but the post is not a study of that file.

**House style.** No external standard covers these — cite them as this
project's conventions:

- The `~40–80` line target and `150` hard ceiling. Real published guidance
  differs: Cursor suggests under 500 lines, Claude Code under 200, Codex stops
  loading instruction files at a combined 32 KiB by default. The numbers here
  are stricter than any of them.
- The `.agents/<vendor>/` unification recipe (see the `project-layout`
  skill).
- The knowledge-cache convention.
- The "do not add a Project structure section" rule.

**Harness config directory.** Paths written `~/.config/<vendor>/…` below mean the
harness's user-level config directory: `~/.config/opencode/` in OpenCode.
Skills live in the shared home `~/.agents/skills/`, which most harnesses read.
Claude Code is the exception. The `project-layout` skill owns the canonical tree.

## Trigger checklist

Surface a suggestion when any of the following is true:

- `AGENTS.md` is missing
- `README.md` is missing or lacks project-specific info (background, problem statement, tech stack)
- No `docs/` directory (or similar) is listed from `README.md` / `AGENTS.md`
- About to make a web lookup in a project with no knowledge cache
- Turn-1 discovery revealed non-obvious conventions an `AGENTS.md` would eliminate
- Spent >2 turns explaining project-specific patterns
- User asks to create, fix, or review a `.gitignore`
- A vendor-specific directory is found at the project root (`.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`, `.windsurf/`, `.continue/`)

`AGENTS.md`, the harness's global rules, and registered `instructions` files load at session start as a shared token budget. Project-level `AGENTS.md` should target ~40–80 lines, with a hard ceiling of 150 lines. Deeper subsystem knowledge belongs in the harness's skills (on-demand) or in `docs/`. The global rules in `~/.agents/rules/` and `~/.agents/rules.personal.d/` are per-session overhead managed separately and do not compete with this budget.

The whole point of these files is **hard-earned context an agent would likely miss without help**. Every line should answer: "Would an agent get this wrong without it?" If not, leave it out. Note the cost: repository context files raise inference cost >20%. They do not reliably improve task success versus no context. The effect holds for human-written and LLM-generated files alike (Gloaguen and others, arXiv:2602.11988). So curation — not volume, and not authorship — is what makes an `AGENTS.md` worth keeping.

## User input

**Always** consider user input (if any) before proceeding. If user input conflicts with Phase 0 facts, prefer user input and flag the discrepancy before drafting.

## Execution phases

### Phase 0: Investigation

Before drafting or editing anything, gather facts from executable sources of truth. Phase 0 applies the priority from the global `local-first.md` rule (which lists the canonical local-source order — do not duplicate that list here) with a tighter lens: it is the priority used specifically to *build* project context, not to answer a question. Add these Phase-0-only sources on top:

- repo-local harness config such as `opencode.json` / `opencode.jsonc`
- `.agents/docs/` for prior cached research and references
- CI workflows and pre-commit / task runner config (these are executable truth that the AGENTS.md must capture)
- existing instruction files (read `AGENTS.md` for content. For vendor files like `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` — treat them as pointers, not sources. If one holds guidance that is not in `AGENTS.md`, ask the user whether to migrate it rather than copying it)

If architecture is still unclear after reading config and docs, inspect a **small number of representative code files**. Use them to find the real entrypoints, package boundaries, and execution flow. Prefer files that show how the system is wired together over random leaf files.

**Prefer executable sources of truth over prose.** If docs conflict with config or scripts, trust the executable source and keep only what you can verify. Never copy a claim into `AGENTS.md` that you could not verify against the repo.

**What to extract** — highest-signal facts for an agent working in this repo:

- exact developer commands, especially non-obvious ones
- how to run a single test, a single package, or a focused verification step
- required command order when it matters, such as `lint → typecheck → test`
- monorepo or multi-package boundaries, ownership of major directories, and the real app/library entrypoints
- framework or toolchain quirks: generated code, migrations, codegen, build artifacts, special env loading, dev servers, infra deploy flow
- repo-specific style or workflow conventions that differ from defaults
- testing quirks: fixtures, integration test prerequisites, snapshot workflows, required services, flaky or expensive suites
- important constraints from existing instruction files worth preserving

Good `AGENTS.md` content is usually hard-earned context that took reading multiple files to infer.

### When the repo can't answer

If Phase 0 leaves gaps that affect correctness, surface them to the user with the harness's question tool, or in plain text. Such gaps are undocumented conventions, branch / release expectations, and missing test prerequisites. Do not ask trivia the repo already answers. Do not ask more than 2–3 facts up front. If the user declines, draft conservatively and mark the gap inline in the proposed `AGENTS.md`.

This is the only place in the skill where clarification questions are encouraged. The cost caveat earlier in the file is the reason: every clarifying question must be high-signal, repo-specific, and unanswerable from `Phase 0` sources.

### Phase 1: AGENTS.md detection

Check for `AGENTS.md` at the workspace root. **Do not duplicate guidance into `CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `.windsurfrules`, or `.github/copilot-instructions.md`** — those are vendor-owned and several tools still read them. If they exist, point them at `AGENTS.md` (for example, Claude Code: `@AGENTS.md` import).

- **A — None exists (clean project)**: suggest a 40–80 line `AGENTS.md` filled from the [template](assets/templates/agents.md), using only facts extracted in Phase 0 and user input if present. Do not invent your own structure. The file may grow toward 150 when keeping guidance co-located helps the project more than fragmenting across supplemental files. Caveat the user that context files are not free upside. They raise inference cost, and they only help when minimal and high-signal. The effect holds for human-written and LLM-generated files alike (Gloaguen and others, arXiv:2602.11988). So the draft must be human-reviewed before commit.
- **B — AGENTS.md exists**: improve it in place rather than rewriting blindly. Preserve verified useful guidance, delete fluff or stale claims, and reconcile it with the current codebase. Offer an update only if stale or incomplete.

### Phase 2: Project documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`). Do not duplicate — add pointer references from `AGENTS.md`. If no docs exist but conventions are non-obvious (security models, API specs, deployment playbooks), suggest narrowly-scoped files in `docs/` — one topic per file. Auto-generated docs do not belong in `docs/`. Put those in a generator output directory or in `.agents/docs/` instead.

#### README.md vs AGENTS.md

Per the [agents.md spec](https://agents.md): `README.md` is for humans (quick starts, project descriptions, contribution norms). `AGENTS.md` complements it with build steps, tests, and conventions that would clutter a README. They are deliberately separate so the human-facing file stays concise and agent-facing guidance stays precise.

**Required pointer**: every `AGENTS.md` must include `README.md` in its `Pointers` section. The README carries the *why* (problem, audience, project intent) and the *how* for humans. The `AGENTS.md` carries the *how* for agents and the *boundaries* (always / ask first / never). Without the pointer, the agent works with only half the picture and risks duplicating or contradicting the README.

README scope, per [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): what the project does, why it is useful, how users get started, where users get help, and who maintains and contributes. The [jehna template](https://github.com/jehna/readme-best-practices) adds license, links, and the section set: Installing, Initial Configuration, Developing, Building, Deploying, Features, Configuration, Contributing, Links, Licensing. Keep it concise — longer material belongs in `docs/` or a wiki, not the README.

If `README.md` is missing, suggest the GitHub five-question template (`what / why / how / help / maintainers`) plus a license pointer. Never duplicate README content into `AGENTS.md`. Reference it instead, and use relative Markdown links so the relationship survives clones.

### Phase 3: Vendor directory unification

Trigger only. The procedure lives in the `project-layout` skill, which owns
the canonical tree and the vendor-unification mechanics. Do not repeat its
steps here.

Two rules matter at this phase:

- **Shared skills** go in `.agents/skills/`. That is the only `.agents/`
  subdirectory a shipped tool scans for skills. The scan list and its
  exceptions live in the `project-layout` skill.
- **Harness-specific assets** — rule files, custom commands, hooks — go in
  `.agents/<vendor-name>/`, reached through the harness's own root directory.

If the symlink is missing when you arrive, recreate it before reading the
vendor config.

### Phase 4: Rules and skills integration

Keep harness-specific content in `.agents/<vendor>/` (or `.<vendor>/` if not yet unified), not in `AGENTS.md`. Add a pointer rule for deep docs. Ensure the harness config lists `~/.agents/rules/*.md` and `~/.agents/rules.personal.d/*.md` under `instructions`. Create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## AGENTS.md template

Use the template at [`assets/templates/agents.md`](assets/templates/agents.md) when suggesting or drafting a new `AGENTS.md`. Drop sections that do not apply. Fill every line from Phase 0 extraction — never from imagination. Do **not** add a "Project structure" or "Architecture overview" section. Agents navigate the tree themselves, and redundant context measurably increases inference cost without reliably improving task success (Gloaguen and others, arXiv:2602.11988).

Use the **3-tier Boundaries** (`✅ Always` / `⚠️ Ask first` / `🚫 Never`). It is the pattern the GitHub Copilot analysis of 2,500+ `agents.md` files found in the best-performing ones (Matt Nigh, github.blog, Nov 2025). The Boundaries section also includes a placeholder `✅ Always` line for **recreating the vendor symlink on fresh clones** (see Phase 3). Use **exact command flags** in the Commands section: `pnpm vitest run -t "name pattern"` is more useful than `pnpm test`. One real code snippet for style beats three paragraphs of style description.

## Knowledge cache

If the project has no knowledge cache, create one with a `README.md` index and reference the cache path from `AGENTS.md` → `Pointers`. For canonical placement, subrole, and naming convention see the `project-layout` skill. For authoring rules (date tag, source, freshness note) see `references/knowledge-cache.md`. For the write-trigger see the global rule `~/.agents/rules/web-verification.md`.

## Writing rules

Include only high-signal, repo-specific guidance: exact commands and shortcuts the agent would otherwise guess wrong. Also include architecture notes that are not obvious from filenames. Include conventions that differ from language or framework defaults, setup requirements, environment quirks, and operational gotchas.

Exclude: generic software advice, long tutorials, exhaustive file trees, obvious language conventions, and speculative claims you could not verify against the repo. Also exclude content better stored in another file referenced via the harness config's `instructions` field, and duplicates of `README.md` / other docs (add pointers instead).

**When in doubt, omit.** Prefer short sections and bullets. If the repo is simple, keep the file simple. If the repo is large, summarize the few structural facts that actually change how an agent should work.

## Style pass on the draft

Before proposing or committing an `AGENTS.md` draft, run the `asd-ste100` skill's Scan Checklist over the prose. Active voice, one idea per sentence, plain words, no marketing adjectives, no run-on sentences joined by semicolons or em dashes.

This skill owns *what to include and what to omit*. `asd-ste100` owns *how the included sentences read*. Load it after the draft is structurally complete. Apply the rewrite, then re-check against this skill's length budget (AGENTS.md targets 40–80 lines, ceiling 150).

## External references

Load these before drafting a new `AGENTS.md` from the template. They justify the template's structure and the writing rules above. Prefer your harness's web-fetch tool over recall. The two arXiv papers are separate studies with different questions, so read them as a pair.

- [AGENTS.md spec](https://agents.md/) — open format, LF/AAIF, 23 agents listed- [A Complete Guide to AGENTS.md](https://gist.github.com/skyzyx/c91d9be9e5050c85e81ccbcca022ff6b) (full guide)
- [Writing a good CLAUDE.md (also applicable to AGENTS.md)](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — progressive disclosure, linters over instructions, under 300 lines as the general consensus and under 60 lines as HumanLayer's own file
- [Writing a Good AGENTS.md](https://www.philschmid.de/writing-good-agents) — ETH Zurich paper summary, what to include vs not
- [`What Goes in AGENTS.md (and What Doesn't)`](https://ro14nd.de/what-goes-in-agents-md/) — empirical checklist, redundant docs hurt more than help. It still says Claude Code cannot read `AGENTS.md` natively, which stopped being true in v2.1.277
- [On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/html/2601.20404v2) — curated `AGENTS.md` gave Codex a 28.64% lower median runtime and 16.58% fewer output tokens. Median total tokens rose 1.29%, and task success was not measured
- [How to Build AGENTS.md (2026) — Augment Code](https://www.augmentcode.com/guides/how-to-build-agents-md) — write only what agents cannot discover independently. It also predates Claude Code's native `AGENTS.md` support
- [Evaluating AGENTS.md — ETH Zurich, arXiv:2602.11988](https://arxiv.org/abs/2602.11988) — Gloaguen and others. The cost caveat: context files raised inference cost by over 20% with no significant task-success gain. Developer-written files beat generated ones by 7%

## Monorepos: nested AGENTS.md

For monorepos, place an `AGENTS.md` inside each package. The agent reads the **closest file to the file being edited**. Subpackage files override the root. Do not duplicate — point to the root and add only the package-specific deltas. Past ~150 lines in the root file, split it up.

## Anti-patterns

See [`references/anti-patterns.md`](references/anti-patterns.md).

## References

- [`assets/templates/agents.md`](assets/templates/agents.md) — copy-as-template for new project `AGENTS.md`. Includes a `✅ Always` placeholder for vendor-symlink recreation.
- [`references/knowledge-cache.md`](references/knowledge-cache.md) — `.agents/docs/cache/` date-tagged web-learned facts cache convention.
- [`references/anti-patterns.md`](references/anti-patterns.md) — checklist of do and do not items for drafting `AGENTS.md`.
- [`references/gitignore-toptal-api.md`](references/gitignore-toptal-api.md) — Toptal gitignore API workflow and pre-seeded template catalog. Use when generating, fixing, or reviewing `.gitignore`.

## Worked scenario

User opens a project. You find: no `AGENTS.md`, a `package.json` with `next@15`, no `.agents/`, no knowledge cache, and a `.cursor/` directory at the root. After ~2 turns of Phase 0 investigation:

> "No `AGENTS.md` and no knowledge cache (see the `project-layout` skill for the canonical layout). Want me to draft a 40-line `AGENTS.md` from the template (Stack / Commands / Boundaries) — and unify `.cursor/` under `.agents/<vendor>/` with a symlink back?"

Short, references the template, surfaces the `AGENTS.md`, the cache (second eager trigger), and the vendor-unification opportunity (Phase 3 trigger).
