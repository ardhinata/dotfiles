# Project Context Setup

When starting work in a project, assess its current agent context and documentation state. Do not modify files automatically — always suggest to the user first.

#### Loading model

AGENTS.md, `.kilo/rules/`, and registered `instructions` files are **all loaded at session start** — treat them as a shared token budget. Keep each file small; collectively they should stay under ~60 lines for typical projects. Move detailed subsystem knowledge to `.kilo/skills/` — skills are truly on-demand: the agent reads the full `SKILL.md` only when a task matches its description.

## Phase 1: AGENTS.md / CLAUDE.md Detection

Check for `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the workspace root.

### Scenario A: Neither exists (clean project)

Suggest a concise (40-60 line), agent-agnostic `AGENTS.md` covering: **Purpose**, **Stack**, **Commands** (test/lint/build flags), **Code style** deviations only, **Project structure**, **Testing**, **Git workflow**, **Boundaries** (never-modify files), and **Pointers** to deeper docs/rules/skills. Use bullets of 1-4 lines each — no paragraphs. Defer detail to pointer-referenced docs or on-demand skills.

Human-written AGENTS.md improves task success by ~4%; LLM-generated fluff hurts performance. Only add sections the agent consistently gets wrong.

### Knowledge Cache

Projects benefit from a **knowledge cache** — a directory for date-tagged facts the agent learned from the web (tool version quirks, API changes, deprecation notices) that future sessions may need again. Reference the cache location from AGENTS.md's **Pointers** section. Common names: `.kilo/cache/`, `.help/`, `docs/cache/`. If absent, suggest creating one during Phase 1. See `web-tools-priority.md` for the caching convention.

### Scenario B: CLAUDE.md exists, no AGENTS.md

`CLAUDE.md` works in Kilo, but `AGENTS.md` follows the [open standard](https://agents.md) and works across more tools. Suggest deriving a slimmer `AGENTS.md` from `CLAUDE.md` (40-60 lines, agent-agnostic) and moving Kilo-specific conventions into `.kilo/rules/`. Complex subsystems can become `.kilo/skills/<name>/SKILL.md`. For external repos, hide `.kilo/` and `AGENTS.md` via `.gitignore` or `.git/info/exclude`.

### Scenario C: AGENTS.md exists

No action needed. Offer an update only if it appears stale or incomplete.

## Phase 2: Project Documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`, `contributing-docs/`). Don't duplicate them — add **pointer references** from AGENTS.md:

```markdown
## References
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
```

Keep AGENTS.md focused on the six core areas; let pointer-referenced docs carry deep reference, loaded on demand.

If no docs exist but the project has non-obvious conventions (security models, API specs, deployment playbooks), suggest narrowly-scoped files (`docs/SECURITY.md`, `docs/QUIRKS.md`, etc.) — one topic per file.

## Phase 3: Rules and Skills Integration

Keep Kilo-specific content in `.kilo/`, not in `AGENTS.md`. Add a pointer rule (e.g. `.kilo/rules/project-docs.md`) for any deep docs, ensure `kilo.jsonc` lists `.kilo/rules/*.md` under `instructions`, and create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## When to Suggest

- First work in a project with no context files
- Discovery work on turn 1 that context files would eliminate
- Non-obvious conventions not visible from the directory structure
- You've spent >2 turns explaining project-specific patterns

Keep suggestions brief — e.g. "This project has no `AGENTS.md` and complex build/test conventions. Want me to draft one?"
