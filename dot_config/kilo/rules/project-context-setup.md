# Project Context Setup

Before deep work in an unfamiliar project — or when context setup would unblock you — load the `project-context-setup` skill. Never modify project context files unilaterally; suggest first.

The goal is a compact instruction file that helps future Kilo sessions avoid mistakes and ramp up quickly. Every line should answer: "Would an agent likely miss this without help?" If not, leave it out. Human-curated, verified content is the whole point — LLM-generated AGENTS.md measurably *reduces* task success and *increases* inference cost (Gloaguen et al., 2026), so investigate the repo (Phase 0) and only write what you can verify.

## Load the skill eagerly when any of these is true

- **Web discovery without a cache.** You're about to call `tavily_search`, `firecrawl_search`, `firecrawl_scrape`, or `context7_*` and the project has no knowledge cache directory (`.tmp/doc-cache/`, `.help/`, `docs/cache/`) — the skill tells you whether to set one up first and what to record.
- **Stuck exploring.** You've spent several turns exploring a project and have no `AGENTS.md` / `CLAUDE.md` / project conventions to anchor on.
- **New project session.** A session is starting in a project you've never seen and you have no orientation document.
- **AGENTS.md / context-file maintenance.** The user asks to update, restructure, split, or modernize `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md`. Also trigger when the user asks to update the documentation cache, knowledge cache, `.help/` directory, or `.tmp/doc-cache/`. Catch-all phrases: "update project structure", "update old AGENTS.md", "update documentation cache", "restructure AGENTS.md", "refresh project docs", "clean up AGENTS.md", "add knowledge cache", "set up .help/", "update context file".

The skill covers: Phase 0 investigation (sourcing order, what to extract, prefer executable truth over prose), AGENTS.md/CLAUDE.md detection phases, project-docs survey, `.kilo/rules/` and `.kilo/skills/` integration, knowledge-cache conventions, writing rules (include/exclude), when to ask the user questions, and "when to suggest" timing.
