# Project Context Setup

When starting work in a project, assess its agent-context and documentation state. Do not modify files automatically — suggest to the user first.

## Loading Model

`AGENTS.md`, `.kilo/rules/`, and registered `instructions` files load at session start — a shared token budget. Keep each file small; collectively under ~60 lines for typical projects. Move detailed subsystem knowledge to `.kilo/skills/` — skills load on demand only when a task matches.

## Phase 1: AGENTS.md / CLAUDE.md Detection

Check for `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the workspace root.

- **A — None exists (clean project)**: suggest a concise (40–60 line), agent-agnostic `AGENTS.md` covering: Purpose, Stack, Commands (test/lint/build flags), Code-style deviations only, Project structure, Testing, Git workflow, Boundaries (never-modify files), Pointers to deeper docs. Bullets of 1–4 lines each. Human-written AGENTS.md improves task success; LLM fluff hurts — only add sections the agent consistently gets wrong.
- **B — CLAUDE.md, no AGENTS.md**: CLAUDE.md works in Kilo, but `AGENTS.md` follows the [open standard](https://agents.md) and works across more tools. Suggest deriving a slimmer `AGENTS.md` (40–60 lines, agent-agnostic) and moving Kilo-specific conventions into `.kilo/rules/`. Complex subsystems → `.kilo/skills/<name>/SKILL.md`. For external repos, hide `.kilo/` and `AGENTS.md` via `.gitignore` / `.git/info/exclude`.
- **C — AGENTS.md exists**: no action. Offer an update only if stale or incomplete.

### Knowledge Cache

Projects benefit from a knowledge-cache dir for date-tagged web-learned facts (tool version quirks, API changes, deprecations). Reference its location from AGENTS.md **Pointers**. Common names: `.kilo/cache/`, `.help/`, `docs/cache/`. If absent, suggest creating one. Caching convention: see `web-tools-priority.md`.

## Phase 2: Project Documentation

Look for existing docs (`CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`). Don't duplicate — add pointer references from AGENTS.md. If no docs exist but conventions are non-obvious (security models, API specs, deployment playbooks), suggest narrowly-scoped files — one topic per file.

## Phase 3: Rules and Skills Integration

Keep Kilo-specific content in `.kilo/`, not in `AGENTS.md`. Add a pointer rule for deep docs; ensure `kilo.jsonc` lists `.kilo/rules/*.md` under `instructions`; create skills for reusable domain patterns (custom build pipelines, proprietary protocols, specialized test setups).

## When to Suggest

- First work in a project with no context files
- Turn-1 discovery that context files would eliminate
- Non-obvious conventions not visible from the directory structure
- You've spent >2 turns explaining project-specific patterns

Keep suggestions brief — e.g. "This project has no `AGENTS.md` and complex build/test conventions. Want me to draft one?"
