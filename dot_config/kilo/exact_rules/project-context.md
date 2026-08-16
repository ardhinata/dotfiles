# Project Context Router

Router rule. Triggers load the `project-context` skill **and** the `project-layout` skill together — both share the same eager-trigger surface (cache check, missing `AGENTS.md`, vendor dir at root) for a fresh project.

## Load both `project-context` AND `project-layout` eagerly when any of these is true

- **Web discovery without a cache.** About to call `tavily_*`, `firecrawl_*`, or `context7_*` in a project with no knowledge cache.
- **Stuck exploring.** Spent several turns exploring a project and have no `AGENTS.md` / project conventions to anchor on.
- **New project session.** Session is starting in a project you've never seen and there is no orientation document.
- **Agent-context maintenance.** User asks to create, update, restructure, split, or modernize `AGENTS.md` or the project's knowledge cache.
- **Vendor directory at the project root.** A `.kilo/`, `.claude/`, `.cursor/`, etc. directory is found.

## Load `project-context` alone (no project-layout trigger)

- AGENTS.md-only standard enforcement (pointing `CLAUDE.md`, `.cursorrules`, `GEMINI.md`, `.windsurfrules` at `AGENTS.md` via `@AGENTS.md` import).
- Drafting or critiquing an `AGENTS.md` against the template at `assets/templates/agents.md` (from the `project-context` skill).
- Triggering the README↔AGENTS.md separation.

## Load `project-layout` alone (no project-context trigger)

- A specific question about where a file lives in a project tree (e.g. "should this go in `.tmp/` or `.agents/docs/cache/`?").
- Vendor path unification mechanics (`ln -s .agents/<vendor> <vendor>`, `.gitignore` patterns).
- Migrating a legacy cache path (`.tmp/doc-cache/`, `.help/`, `docs/cache/`) to the canonical `.agents/docs/cache/`.

## Why a router

`project-context` and `project-layout` were originally one skill (`project-context` covered both AGENTS.md lifecycle and on-disk layout). The split enforces a single source of truth per concern:

- AGENTS.md content, README↔AGENTS separation, vendoring *trigger* → `project-context`
- On-disk tree, `.tmp/` subroles, vendor path *mechanics*, knowledge-cache placement → `project-layout`
- Per-doc-type filename, frontmatter, section order → `document-conventions` (load via the `document-conventions` rule)

Do not modify these skill descriptions to overlap. If a question fits two concerns, load both skills.