---
name: project-context-setup
description: Project context and documentation setup. Activated when starting work in an unfamiliar project, when an AGENTS.md/CLAUDE.md would unblock progress, or before web discovery tools run in a project that lacks a knowledge cache (`.tmp/doc-cache/`, `.help/`, `docs/cache/`).
---

# Project Context Setup

When starting work in a project, assess its agent-context and documentation state. Do not modify files automatically — suggest to the user first.

`AGENTS.md`, `.kilo/rules/`, and registered `instructions` files load at session start as a shared token budget. Project-level `AGENTS.md` should stay under ~60 lines; deeper subsystem knowledge belongs in `.kilo/skills/` (on-demand). Kilo's own rules in `~/.config/kilo/rules/` are per-session overhead managed separately and do not compete with this budget.

The whole point of these files is **hard-earned context an agent would likely miss without help**. Every line should answer: "Would an agent get this wrong without it?" If not, leave it out. Note the cost: even human-written repository context files raise inference cost >20% and do not reliably improve task success vs no context; LLM-generated files are worse (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988). So curation — not volume — is what makes an AGENTS.md worth keeping.

## Phase 0: Investigation

Before drafting or editing anything, gather facts from executable sources of truth. Read the highest-value sources first, in roughly this order:

- `README*`, root manifests, workspace config, lockfiles
- build, test, lint, formatter, typecheck, and codegen config
- CI workflows and pre-commit / task runner config
- existing instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`)
- repo-local Kilo config such as `kilo.json` / `kilo.jsonc`

If architecture is still unclear after reading config and docs, inspect a **small number of representative code files** to find the real entrypoints, package boundaries, and execution flow. Prefer files that show how the system is wired together over random leaf files.

**Prefer executable sources of truth over prose.** If docs conflict with config or scripts, trust the executable source and keep only what you can verify. Never copy a claim into `AGENTS.md` that you could not verify against the repo.

### What to extract

Look for the highest-signal facts for an agent working in this repo:

- exact developer commands, especially non-obvious ones
- how to run a single test, a single package, or a focused verification step
- required command order when it matters, such as `lint -> typecheck -> test`
- monorepo or multi-package boundaries, ownership of major directories, and the real app/library entrypoints
- framework or toolchain quirks: generated code, migrations, codegen, build artifacts, special env loading, dev servers, infra deploy flow
- repo-specific style or workflow conventions that differ from defaults
- testing quirks: fixtures, integration test prerequisites, snapshot workflows, required services, flaky or expensive suites
- important constraints from existing instruction files worth preserving

Good `AGENTS.md` content is usually hard-earned context that took reading multiple files to infer.

## Phase 1: AGENTS.md / CLAUDE.md Detection

Check for `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the workspace root.

- **A — None exists (clean project)**: suggest a 40–60 line `AGENTS.md` filled from the **template below**, using only facts extracted in Phase 0. Do not invent your own structure. Caveat the user that context files are not free upside — they raise inference cost and only help when minimal and high-signal (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988); LLM-generated files specifically reduce task success, so the draft must be human-reviewed before commit.
- **B — CLAUDE.md, no AGENTS.md**: CLAUDE.md works in Kilo, but `AGENTS.md` follows the [open standard](https://agents.md) (donated to the Agentic AI Foundation / Linux Foundation, Dec 2025; 60,000+ repos) and works across more tools. Suggest deriving a slimmer `AGENTS.md` (40–60 lines, agent-agnostic) and moving Kilo-specific conventions into `.kilo/rules/`. Complex subsystems → `.kilo/skills/<name>/SKILL.md`. For external repos, hide `.kilo/` and `AGENTS.md` via `.gitignore` / `.git/info/exclude`.
- **C — AGENTS.md exists**: improve it in place rather than rewriting blindly. Preserve verified useful guidance, delete fluff or stale claims, and reconcile it with the current codebase. Offer an update only if stale or incomplete.

### Knowledge Cache

Projects benefit from a knowledge-cache dir for date-tagged web-learned facts (tool version quirks, API changes, deprecations). Reference its location from AGENTS.md **Pointers**. Common names: `.tmp/doc-cache/`, `.help/`, `docs/cache/`. If absent, suggest creating one. Caching convention: see `web-tools-priority.md`.

**When to act on the cache:**
- About to call `tavily_search`, `firecrawl_search`, `firecrawl_scrape`, or `context7_*` for the first time in this project → check the cache dir first; if missing or empty, surface that to the user and suggest a quick pointer add to AGENTS.md *before* burning web-tool credits.
- The cache hit is a prior fetch tagged with a date — re-verify if the domain is volatile (CLI tool / framework API released < 6 months ago).
- Entry naming: `cache/<topic>/YYYY-MM-DD-<short-slug>.md` — one topic per file, ISO date prefix so the tree sorts chronologically.

## AGENTS.md Template

Use this skeleton when suggesting or drafting a new `AGENTS.md`. Drop sections that do not apply. Fill every line from Phase 0 extraction — never from imagination. Do **not** add a "Project structure" or "Architecture overview" section — agents navigate the tree themselves, and those sections measurably increase inference cost without improving task success (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988).

```markdown
# AGENTS.md

## Purpose
<one sentence: what the project is>

## Stack
- Language / runtime: <e.g. TypeScript 5.7, Node 22>
- Framework: <e.g. Next.js 15 App Router>
- Package manager: <e.g. pnpm only — never npm/yarn>
- Lockfile: <e.g. pnpm-lock.yaml>

## Commands
- Install: `pnpm install`
- Dev: `pnpm dev`
- Build: `pnpm build`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Test all: `pnpm test`
- Test one file: `pnpm vitest run path/to/file.test.ts`
- Test by name: `pnpm vitest run -t "name pattern"`

## Code style
[one real code snippet from this codebase that exemplifies the dominant style — beats three paragraphs describing it]
- <e.g. named exports only, no defaults>
- <e.g. files under 300 lines>

## Testing rules
- <e.g. unit tests for every new function>
- <e.g. mock external services at the boundary>

## Boundaries
### ✅ Always
- <e.g. run lint + typecheck before commit>
- <e.g. list only human authors in git commits>

### ⚠️ Ask first
- <e.g. database schema changes>
- <e.g. new top-level dependencies>
- <e.g. deleting files>

### 🚫 Never
- <e.g. commit secrets, `.env`, credentials>
- <e.g. force-push to main>
- <e.g. modify `vendor/`, `dist/`, `build/`>

## Pointers
- Deeper docs: `<relative/path/to/ARCHITECTURE.md>`
- Conventions: `<relative/path/to/CONTRIBUTING.md>`
- Knowledge cache: `.tmp/doc-cache/` (see `web-tools-priority` rule)
```

Use the **3-tier Boundaries** (`✅ Always` / `⚠️ Ask first` / `🚫 Never`) — it is the pattern the GitHub Copilot analysis of 2,500+ `agents.md` files found in the best-performing ones (Matt Nigh, github.blog, Nov 2025). Use **exact command flags** in the Commands section: `pnpm vitest run -t "name pattern"` is more useful than `pnpm test`. One real code snippet for style beats three paragraphs of style description.

## Writing rules

Include only high-signal, repo-specific guidance such as:

- exact commands and shortcuts the agent would otherwise guess wrong
- architecture notes that are not obvious from filenames
- conventions that differ from language or framework defaults
- setup requirements, environment quirks, and operational gotchas
- references to existing instruction sources that matter

Exclude:

- generic software advice
- long tutorials or exhaustive file trees
- obvious language conventions
- speculative claims or anything you could not verify against the repo
- content better stored in another file referenced via `kilo.jsonc` `instructions`
- duplicate content that already lives in `README.md` or other docs — add pointers instead

**When in doubt, omit.** Prefer short sections and bullets. If the repo is simple, keep the file simple. If the repo is large, summarize the few structural facts that actually change how an agent should work.

## Monorepos: nested AGENTS.md

For monorepos, place an `AGENTS.md` inside each package. The agent reads the **closest file to the file being edited**; subpackage files override the root. Do not duplicate — point to the root and add only the package-specific deltas. Past ~150–200 lines in the root file, split it up.

## Anti-patterns

- **Do not auto-generate** with `/init` or equivalents and commit the output blind. Repository context files — human- or LLM-written — raise inference cost by over 20% and tend to reduce task success vs no context; LLM-generated files reduce it further (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988). Human-curated, verified, minimal content is the only thing that earns the cost.
- **Do not add a Project structure or Architecture overview section.** Agents navigate the tree themselves; restating it costs tokens without helping.
- **Do not append rules reactively** ("add another rule when the agent makes a mistake"). Prune stale rules. Drift-and-append is the most common failure mode.
- **Do not exceed 60 lines** in the root AGENTS.md. Past that, split into nested files.
- **Do not duplicate content that already lives in `README.md` or other docs.** Add pointers instead.

## Questions

Only ask the user questions if the repo cannot answer something important. Use the `question` tool for one short batch at most.

Good questions:

- undocumented team conventions
- branch / PR / release expectations
- missing setup or test prerequisites that are known but not written down

Do not ask about anything the repo already makes clear.

## Phase 2: Project Documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`). Do not duplicate — add pointer references from AGENTS.md. If no docs exist but conventions are non-obvious (security models, API specs, deployment playbooks), suggest narrowly-scoped files — one topic per file.

## Phase 3: Rules and Skills Integration

Keep Kilo-specific content in `.kilo/`, not in `AGENTS.md`. Add a pointer rule for deep docs; ensure `kilo.jsonc` lists `.kilo/rules/*.md` under `instructions`; create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## When to Suggest

- First work in a project with no context files
- Turn-1 discovery that context files would eliminate
- Non-obvious conventions not visible from the directory structure
- You have spent >2 turns explaining project-specific patterns
- A web discovery tool is about to be called and no knowledge cache exists

Keep suggestions brief — e.g. "This project has no `AGENTS.md` and complex build/test conventions. Want me to draft one from the template?"

## Worked Scenario

User opens a project. You find: no `AGENTS.md`, a `package.json` with `next@15`, no `.kilo/`, no knowledge cache. After ~2 turns of Phase 0 investigation:

> "No `AGENTS.md` and no `.tmp/doc-cache/`. Want me to draft a 40-line `AGENTS.md` from the template (Stack / Commands / Boundaries) and add a `.tmp/doc-cache/` pointer so future web fetches get cached here?"

Short, references the template, surfaces both the AGENTS.md and the cache (the second eager trigger).
