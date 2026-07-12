---
name: project-context
description: Project agent-context and documentation convention. Use when starting work in a project that lacks AGENTS.md/CLAUDE.md or a standardized docs directory, or when about to fetch external info via tavily/firecrawl/context7 in a project that has no knowledge cache (`.help/`, `.tmp/doc-cache/`).
---

# Project Context

When starting work in a project, assess its agent-context and documentation state. When the project lacks agent-context or a standardized project document, suggest creating, fixing, or optimizing it.

## Trigger checklist

Surface a suggestion when any of the following is true:

- `AGENTS.md` or `CLAUDE.md` is missing
- `README.md` is missing or lacks project-specific info (background, problem statement, tech stack)
- No `docs/` directory (or similar) is listed from `README.md` / `AGENTS.md`
- About to call `tavily_*`, `firecrawl_*`, or `context7_*` for the first time in a project with no knowledge cache
- Turn-1 discovery revealed non-obvious conventions an `AGENTS.md` would eliminate
- Spent >2 turns explaining project-specific patterns

`AGENTS.md`, `.kilo/rules/`, and registered `instructions` files load at session start as a shared token budget. Project-level `AGENTS.md` should stay under ~60 lines; deeper subsystem knowledge belongs in `.kilo/skills/` (on-demand). Kilo's own rules in `~/.config/kilo/rules/` are per-session overhead managed separately and do not compete with this budget.

The whole point of these files is **hard-earned context an agent would likely miss without help**. Every line should answer: "Would an agent get this wrong without it?" If not, leave it out. Note the cost: even human-written repository context files raise inference cost >20% and do not reliably improve task success vs no context; LLM-generated files are worse (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988). So curation — not volume — is what makes an `AGENTS.md` worth keeping.

## User input

**Always** consider user input (if any) before proceeding. If user input conflicts with Phase 0 facts, prefer user input and flag the discrepancy before drafting.

```text
$ARGUMENTS
```

## Execution phases

### Phase 0: Investigation

Before drafting or editing anything, gather facts from executable sources of truth. Read the highest-value sources first, in roughly this order:

- `README*`, root manifests, workspace config, lockfiles
- build, test, lint, formatter, typecheck, and codegen config
- CI workflows and pre-commit / task runner config
- existing instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`)
- repo-local Kilo config such as `kilo.json` / `kilo.jsonc`

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

### Phase 1: AGENTS.md / CLAUDE.md Detection

Check for `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the workspace root.

- **A — None exists (clean project)**: suggest a 40–60 line `AGENTS.md` filled from the [template](references/AGENTS.md), using only facts extracted in Phase 0 and user input if present. Do not invent your own structure. Caveat the user that context files are not free upside — they raise inference cost and only help when minimal and high-signal (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988); LLM-generated files specifically reduce task success, so the draft must be human-reviewed before commit.
- **B — CLAUDE.md, no AGENTS.md**: `AGENTS.md` follows the [open standard](https://agents.md) (donated to the Agentic AI Foundation / Linux Foundation, Dec 2025; 60,000+ repos) and works across more tools. Suggest deriving a slimmer `AGENTS.md` (40–60 lines, agent-agnostic) and moving Kilo-specific conventions into `.kilo/rules/`. Complex subsystems → `.kilo/skills/<name>/SKILL.md`. For external repos, hide `.kilo/` and `AGENTS.md` via `.gitignore` / `.git/info/exclude`.
- **C — AGENTS.md exists**: improve it in place rather than rewriting blindly. Preserve verified useful guidance, delete fluff or stale claims, and reconcile it with the current codebase. Offer an update only if stale or incomplete.

### Phase 2: Project Documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`). Do not duplicate — add pointer references from `AGENTS.md`. If no docs exist but conventions are non-obvious (security models, API specs, deployment playbooks), suggest narrowly-scoped files — one topic per file.

#### README.md vs AGENTS.md

Per the [agents.md spec](https://agents.md): `README.md` is for humans (quick starts, project descriptions, contribution norms); `AGENTS.md` complements it with build steps, tests, and conventions that would clutter a README. They are deliberately separate so the human-facing file stays concise and agent-facing guidance stays precise.

**Required pointer**: every `AGENTS.md` must include `README.md` in its `Pointers` section. The README carries the *why* (problem, audience, project intent) and the *how* for humans; the `AGENTS.md` carries the *how* for agents and the *boundaries* (always / ask first / never). Without the pointer, the agent works with only half the picture and risks duplicating or contradicting the README.

README scope, per [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) and the [jehna template](https://github.com/jehna/readme-best-practices): what the project does, why it's useful, how to get started, where to get help, who maintains and contributes, license, and links. Recommended sections: Getting started, Installing, Developing, Features, Configuration, Contributing, Links, Licensing. Keep it concise — longer material belongs in `docs/` or a wiki, not the README.

If `README.md` is missing, suggest the GitHub five-question template (`what / why / how / help / maintainers`) plus a license pointer. Never duplicate README content into `AGENTS.md`; reference it instead, and use relative Markdown links so the relationship survives clones.

### Phase 3: Rules and Skills Integration

Keep Kilo-specific content in `.kilo/`, not in `AGENTS.md`. Add a pointer rule for deep docs; ensure `kilo.jsonc` lists `.kilo/rules/*.md` under `instructions`; create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## AGENTS.md Template

Use the template at [`references/AGENTS.md`](references/AGENTS.md) when suggesting or drafting a new `AGENTS.md`. Drop sections that do not apply. Fill every line from Phase 0 extraction — never from imagination. Do **not** add a "Project structure" or "Architecture overview" section — agents navigate the tree themselves, and those sections measurably increase inference cost without improving task success (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988).

Use the **3-tier Boundaries** (`✅ Always` / `⚠️ Ask first` / `🚫 Never`) — it is the pattern the GitHub Copilot analysis of 2,500+ `agents.md` files found in the best-performing ones (Matt Nigh, github.blog, Nov 2025). Use **exact command flags** in the Commands section: `pnpm vitest run -t "name pattern"` is more useful than `pnpm test`. One real code snippet for style beats three paragraphs of style description.

## Knowledge cache

If the project has no knowledge cache for date-tagged web-learned facts, suggest creating one and referencing it from `AGENTS.md` → `Pointers`. Conventions: see `references/knowledge-cache.md` and the global rule `~/.config/kilo/rules/web-tools-priority.md`.

## Writing rules

Include only high-signal, repo-specific guidance: exact commands and shortcuts the agent would otherwise guess wrong, architecture notes that are not obvious from filenames, conventions that differ from language or framework defaults, setup requirements, environment quirks, and operational gotchas.

Exclude: generic software advice, long tutorials, exhaustive file trees, obvious language conventions, speculative claims you could not verify against the repo, content better stored in another file referenced via `kilo.jsonc` `instructions`, and duplicates of `README.md` / other docs (add pointers instead).

**When in doubt, omit.** Prefer short sections and bullets. If the repo is simple, keep the file simple. If the repo is large, summarize the few structural facts that actually change how an agent should work.

## Monorepos: nested AGENTS.md

For monorepos, place an `AGENTS.md` inside each package. The agent reads the **closest file to the file being edited**; subpackage files override the root. Do not duplicate — point to the root and add only the package-specific deltas. Past ~150–200 lines in the root file, split it up.

## Anti-patterns

See [`references/anti-patterns.md`](references/anti-patterns.md).

## Worked scenario

User opens a project. You find: no `AGENTS.md`, a `package.json` with `next@15`, no `.kilo/`, no knowledge cache. After ~2 turns of Phase 0 investigation:

> "No `AGENTS.md` and no `.tmp/doc-cache/`. Want me to draft a 40-line `AGENTS.md` from the template (Stack / Commands / Boundaries) and add a `.tmp/doc-cache/` pointer so future web fetches get cached here?"

Short, references the template, surfaces both the `AGENTS.md` and the cache (the second eager trigger).
