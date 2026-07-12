# Project Context

Load the `project-context` skill before deep work in an unfamiliar project — or when context setup would unblock you. Never modify project context files unilaterally; suggest first.

The goal is a compact instruction file that helps future Kilo sessions avoid mistakes and ramp up quickly. Every line should answer: "Would an agent likely miss this without help?" If not, leave it out. Human-curated, verified content is the whole point — LLM-generated AGENTS.md measurably *reduces* task success and *increases* inference cost (Gloaguen et al., 2026), so investigate the repo (Phase 0) and only write what you can verify.

## Load the skill eagerly when any of these is true

- **Web discovery without a cache.** About to call `tavily_*`, `firecrawl_*`, or `context7_*` in a project with no knowledge cache directory (`.tmp/doc-cache/`, `.help/`, `docs/cache/`) — the skill tells you whether to set one up first and what to record.
- **Stuck exploring.** Spent several turns exploring a project and have no `AGENTS.md` / `CLAUDE.md` / project conventions to anchor on.
- **New project session.** Session is starting in a project you've never seen and you have no orientation document.
- **Agent-context maintenance.** User asks to create, update, restructure, split, or modernize `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, or the project's knowledge cache.

The skill covers: Phase 0 investigation (sourcing order, what to extract, prefer executable truth over prose), AGENTS.md/CLAUDE.md detection, README↔AGENTS.md separation, `.kilo/rules/` and `.kilo/skills/` integration, knowledge-cache conventions, writing rules (include/exclude), when to ask the user questions, and "when to suggest" timing.