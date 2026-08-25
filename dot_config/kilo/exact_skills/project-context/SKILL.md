---
name: project-context
description: Project-level agent guidance and the AGENTS.md lifecycle. Use when starting work in a project that lacks `AGENTS.md`, when discovering non-obvious project conventions an AGENTS.md would eliminate, when a vendor-specific directory (`.kilo/`, `.claude/`, `.cursor/`, etc.) is found at the project root, or when integrating Kilo rules and skills under `.agents/kilo/`. Treats `AGENTS.md` as the only agent instruction standard — ignores vendor-specific files like `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `GEMINI.md`. For project directory layout, `.tmp/` subroles, vendor path unification, and knowledge-cache placement, load the `project-layout` skill instead.
---

# Project Context

When starting work in a project, assess its agent-context and documentation state. When the project lacks agent-context, a standardized documentation layout, or a knowledge cache, **suggest** (do not auto-write) creating, fixing, or optimizing it.

## Standard directory layout

For the canonical on-disk layout of an agentic-driven project (`AGENTS.md`, `README.md`, `docs/`, `.agents/`, `.agents/docs/cache/`, `.tmp/{notes,plans}/`, vendor unification), **load the `project-layout` skill**. This skill owns the AGENTS.md lifecycle and README↔AGENTS separation; the layout itself is a single source of truth in `project-layout`.

## Proactive caching default

After any web lookup that produces reusable or volatile information, write a date-tagged entry under the project's knowledge cache (see the `project-layout` skill for canonical placement and naming) and update its `README.md` index. Prefer verified web sources over training-data recall. This is a global default, not a per-project `AGENTS.md` directive.

## AGENTS.md-only standard

`AGENTS.md` is the open format stewarded by the [Agentic AI Foundation](https://aaif.io/projects/agents-md/) under the Linux Foundation (Dec 2025); it works across 30+ agents (Codex, Claude Code via `@AGENTS.md`, Cursor, Copilot, Aider, opencode, Zed, Warp, etc.). **Treat `AGENTS.md` as the only agent instruction standard.** Do not write to, copy from, or rely on `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules`, `GEMINI.md`, etc. — when present, point them at `AGENTS.md` via an import (`@AGENTS.md`) so one canonical file drives every tool. New work goes in `AGENTS.md`; vendor-specific overrides belong in `.agents/<vendor>/`.

## Trigger checklist

Surface a suggestion when any of the following is true:

- `AGENTS.md` is missing
- `README.md` is missing or lacks project-specific info (background, problem statement, tech stack)
- No `docs/` directory (or similar) is listed from `README.md` / `AGENTS.md`
- About to call `tavily_*`, `firecrawl_*`, or `context7_*` for the first time in a project with no knowledge cache
- Turn-1 discovery revealed non-obvious conventions an `AGENTS.md` would eliminate
- Spent >2 turns explaining project-specific patterns
- User asks to create, fix, or review a `.gitignore`
- A vendor-specific directory is found at the project root (`.kilo/`, `.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`, `.windsurf/`, `.continue/`)

`AGENTS.md`, `.kilo/rules/`, and registered `instructions` files load at session start as a shared token budget. Project-level `AGENTS.md` should target ~40–80 lines, hard ceiling 150 lines; deeper subsystem knowledge belongs in `.kilo/skills/` (on-demand) or in `docs/`. Kilo's own rules in `~/.config/kilo/rules/` are per-session overhead managed separately and do not compete with this budget.

The whole point of these files is **hard-earned context an agent would likely miss without help**. Every line should answer: "Would an agent get this wrong without it?" If not, leave it out. Note the cost: even human-written repository context files raise inference cost >20% and do not reliably improve task success vs no context; LLM-generated files are worse (Gloaguen et al., arXiv:2602.11988). So curation — not volume — is what makes an `AGENTS.md` worth keeping.

## User input

**Always** consider user input (if any) before proceeding. If user input conflicts with Phase 0 facts, prefer user input and flag the discrepancy before drafting.

```text
$ARGUMENTS
```

## Execution phases

### Phase 0: Investigation

Before drafting or editing anything, gather facts from executable sources of truth. Phase 0 applies the priority from the global `local-first.md` rule (which lists the canonical local-source order — do not duplicate that list here) with a tighter lens: it is the priority used specifically to *build* project context, not to answer a question. Add these Phase-0-only sources on top:

- repo-local Kilo config such as `kilo.json` / `kilo.jsonc`
- `.agents/docs/` for prior cached research and references
- CI workflows and pre-commit / task runner config (these are executable truth that the AGENTS.md must capture)
- existing instruction files (only read `AGENTS.md`; ignore vendor-specific files like `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md` — they are out of scope per the AGENTS.md-only rule above)

If architecture is still unclear after reading config and docs, inspect a **small number of representative code files** to find the real entrypoints, package boundaries, and execution flow. Prefer files that show how the system is wired together over random leaf files.

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

If Phase 0 leaves gaps that affect correctness — undocumented conventions, branch / release expectations, missing test prerequisites — surface them to the user with the `question` tool as one short batch. Do not ask trivia the repo already answers; do not ask more than 2–3 facts up front. If the user declines, draft conservatively and mark the gap inline in the proposed `AGENTS.md`.

This is the only place in the skill where clarification questions are encouraged. The cost caveat earlier in the file is the reason: every clarifying question must be high-signal, repo-specific, and unanswerable from `Phase 0` sources.

### Phase 1: AGENTS.md detection

Check for `AGENTS.md` at the workspace root. **Ignore `CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `.windsurfrules`, `.github/copilot-instructions.md`** — they are not part of the standard. If they exist, point them at `AGENTS.md` (e.g. Claude Code: `@AGENTS.md` import).

- **A — None exists (clean project)**: suggest a 40–80 line `AGENTS.md` filled from the [template](assets/templates/agents.md), using only facts extracted in Phase 0 and user input if present. Do not invent your own structure. The file may grow toward 150 when keeping guidance co-located helps the project more than fragmenting across supplemental files. Caveat the user that context files are not free upside — they raise inference cost and only help when minimal and high-signal (Gloaguen et al., arXiv:2602.11988); LLM-generated files specifically reduce task success, so the draft must be human-reviewed before commit.
- **B — AGENTS.md exists**: improve it in place rather than rewriting blindly. Preserve verified useful guidance, delete fluff or stale claims, and reconcile it with the current codebase. Offer an update only if stale or incomplete.

### Phase 2: Project documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`). Do not duplicate — add pointer references from `AGENTS.md`. If no docs exist but conventions are non-obvious (security models, API specs, deployment playbooks), suggest narrowly-scoped files in `docs/` — one topic per file. Auto-generated docs do not belong in `docs/`; put those in a generator output directory or in `.agents/docs/` instead.

#### README.md vs AGENTS.md

Per the [agents.md spec](https://agents.md): `README.md` is for humans (quick starts, project descriptions, contribution norms); `AGENTS.md` complements it with build steps, tests, and conventions that would clutter a README. They are deliberately separate so the human-facing file stays concise and agent-facing guidance stays precise.

**Required pointer**: every `AGENTS.md` must include `README.md` in its `Pointers` section. The README carries the *why* (problem, audience, project intent) and the *how* for humans; the `AGENTS.md` carries the *how* for agents and the *boundaries* (always / ask first / never). Without the pointer, the agent works with only half the picture and risks duplicating or contradicting the README.

README scope, per [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) and the [jehna template](https://github.com/jehna/readme-best-practices): what the project does, why it's useful, how to get started, where to get help, who maintains and contributes, license, and links. Recommended sections: Getting started, Installing, Developing, Features, Configuration, Contributing, Links, Licensing. Keep it concise — longer material belongs in `docs/` or a wiki, not the README.

If `README.md` is missing, suggest the GitHub five-question template (`what / why / how / help / maintainers`) plus a license pointer. Never duplicate README content into `AGENTS.md`; reference it instead, and use relative Markdown links so the relationship survives clones.

### Phase 3: Vendor directory unification

When the project root contains a vendor-specific directory (`.kilo/`, `.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`, `.windsurf/`, `.continue/`, etc.):

1. Move its contents to `.agents/<vendor-name>/` (e.g. `.kilo/` → `.agents/kilo/`).
2. Create a symlink `<vendor-name>/` → `.agents/<vendor-name>/` at the project root so vendor tools keep finding their config.
3. Add the symlink pattern to `.gitignore` so it is not committed.
4. Add a `✅ Always` rule to `AGENTS.md` > Boundaries stating: *recreate the symlink if it is missing on a fresh clone* (i.e. `ln -s .agents/<vendor> <vendor>`).

If the symlink is missing when you arrive, recreate it before reading the vendor config.

### Phase 4: Rules and skills integration

Keep Kilo-specific content in `.agents/kilo/` (or `.kilo/` if not yet unified), not in `AGENTS.md`. Add a pointer rule for deep docs; ensure `kilo.jsonc` lists `~/.config/kilo/rules/*.md` under `instructions`; create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## AGENTS.md template

Use the template at [`assets/templates/agents.md`](assets/templates/agents.md) when suggesting or drafting a new `AGENTS.md`. Drop sections that do not apply. Fill every line from Phase 0 extraction — never from imagination. Do **not** add a "Project structure" or "Architecture overview" section — agents navigate the tree themselves, and those sections measurably increase inference cost without improving task success (Gloaguen et al., arXiv:2602.11988).

Use the **3-tier Boundaries** (`✅ Always` / `⚠️ Ask first` / `🚫 Never`) — it is the pattern the GitHub Copilot analysis of 2,500+ `agents.md` files found in the best-performing ones (Matt Nigh, github.blog, Nov 2025). The Boundaries section also includes a placeholder `✅ Always` line for **recreating the vendor symlink on fresh clones** (see Phase 3). Use **exact command flags** in the Commands section: `pnpm vitest run -t "name pattern"` is more useful than `pnpm test`. One real code snippet for style beats three paragraphs of style description.

## Knowledge cache

If the project has no knowledge cache, suggest creating one with a `README.md` index and referencing the cache path from `AGENTS.md` → `Pointers`. For canonical placement, subrole, and naming convention see the `project-layout` skill; for authoring rules (date tag, source, freshness note) see `references/knowledge-cache.md`; for the write-trigger see the global rule `~/.config/kilo/rules/web-tools-priority.md`.

## Writing rules

Include only high-signal, repo-specific guidance: exact commands and shortcuts the agent would otherwise guess wrong, architecture notes that are not obvious from filenames, conventions that differ from language or framework defaults, setup requirements, environment quirks, and operational gotchas.

Exclude: generic software advice, long tutorials, exhaustive file trees, obvious language conventions, speculative claims you could not verify against the repo, content better stored in another file referenced via `kilo.jsonc` `instructions`, and duplicates of `README.md` / other docs (add pointers instead).

**When in doubt, omit.** Prefer short sections and bullets. If the repo is simple, keep the file simple. If the repo is large, summarize the few structural facts that actually change how an agent should work.

## Style pass on the draft

Before proposing or committing an `AGENTS.md` draft, run the `asd-ste100` skill's Scan Checklist over the prose. Active voice, one idea per sentence, plain words, no marketing adjectives, no run-on sentences joined by semicolons or em dashes.

This skill owns *what to include and what to omit*. `asd-ste100` owns *how the included sentences read*. Load it after the draft is structurally complete; apply the rewrite, then re-check against this skill's length budget (AGENTS.md targets 40–80 lines, ceiling 150).

## External references

Load these before drafting a new `AGENTS.md` from the template — they justify the template's structure and the writing rules above. Prefer `webfetch` over memory; the AGENTS.md-impact paper in particular informs the "every line must earn its place" stance.

- [AGENTS.md spec](https://agents.md/) — open format, LF/AAIF, 30+ agents
- [A Complete Guide to AGENTS.md](https://gist.github.com/skyzyx/c91d9be9e5050c85e81ccbcca022ff6b) (full guide)
- [Writing a good CLAUDE.md (also applicable to AGENTS.md)](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — progressive disclosure, <60 lines, linters over instructions
- [Writing a Good AGENTS.md](https://www.philschmid.de/writing-good-agents) — ETH Zurich paper summary, what to include vs not
- [What Goes in AGENTS.md (and What Doesn't)](https://ro14nd.de/what-goes-in-agents-md/) — empirical checklist, redundant docs hurt more than help
- [On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/html/2601.20404v2) — curated minimal files cut wall-clock 28% and output tokens 16%
- [How to Build AGENTS.md (2026) — Augment Code](https://www.augmentcode.com/guides/how-to-build-agents-md) — write only what agents cannot discover independently
- [Evaluating AGENTS.md — ETH Zurich, arXiv:2602.11988](https://arxiv.org/abs/2602.11988) — Gloaguen et al.; the LLM-generated AGENTS.md source for the cost caveat

## Monorepos: nested AGENTS.md

For monorepos, place an `AGENTS.md` inside each package. The agent reads the **closest file to the file being edited**; subpackage files override the root. Do not duplicate — point to the root and add only the package-specific deltas. Past ~150 lines in the root file, split it up.

## Anti-patterns

See [`references/anti-patterns.md`](references/anti-patterns.md).

## References

- [`assets/templates/agents.md`](assets/templates/agents.md) — copy-as-template for new project `AGENTS.md`. Includes a `✅ Always` placeholder for vendor-symlink recreation.
- [`references/knowledge-cache.md`](references/knowledge-cache.md) — `.agents/docs/cache/` date-tagged web-learned facts cache convention.
- [`references/anti-patterns.md`](references/anti-patterns.md) — do/don't checklist for drafting `AGENTS.md`.
- [`references/gitignore-toptal-api.md`](references/gitignore-toptal-api.md) — Toptal gitignore API workflow and pre-seeded template catalog. Use when generating, fixing, or reviewing `.gitignore`.

## Worked scenario

User opens a project. You find: no `AGENTS.md`, a `package.json` with `next@15`, no `.agents/`, no knowledge cache, and a `.kilo/` directory at the root. After ~2 turns of Phase 0 investigation:

> "No `AGENTS.md` and no knowledge cache (see the `project-layout` skill for the canonical layout). Want me to draft a 40-line `AGENTS.md` from the template (Stack / Commands / Boundaries) — and unify `.kilo/` under `.agents/kilo/` with a symlink back?"

Short, references the template, surfaces the `AGENTS.md`, the cache (second eager trigger), and the vendor-unification opportunity (Phase 3 trigger).
