# Project Context

Load the `project-context` skill before deep work in an unfamiliar project — or when context setup would unblock you. Never modify project context files unilaterally; suggest first.

The goal is a compact instruction file that helps future Kilo sessions avoid mistakes and ramp up quickly. Every line should answer: "Would an agent likely miss this without help?" If not, leave it out. Human-curated, verified content is the whole point — LLM-generated AGENTS.md measurably *reduces* task success and *increases* inference cost >20% (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988), so investigate the repo (Phase 0) and only write what you can verify.

`AGENTS.md` is the only agent instruction standard. Treat `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `GEMINI.md`, `.github/copilot-instructions.md` as out of scope — context must stay portable and agent-agnostic. If a vendor directory (`.kilo/`, `.kiro/`, `.claude/`, `.opencode/`, `.cursor/`, `.aider/`, `.windsurf/`, `.continue/`) exists at the project root, the skill will suggest unifying it under `.agents/<vendor>/` with a symlink back.

## Load the skill eagerly when any of these is true

- **Web discovery without a cache.** About to call `tavily_*`, `firecrawl_*`, or `context7_*` in a project with no knowledge cache directory — prefer `.agents/docs/cache/`; legacy `.tmp/doc-cache/` or `.help/` are acceptable fallbacks. The skill tells you whether to set one up first and what to record.
- **Stuck exploring.** Spent several turns exploring a project and have no `AGENTS.md` / project conventions to anchor on.
- **New project session.** Session is starting in a project you've never seen and you have no orientation document.
- **Agent-context maintenance.** User asks to create, update, restructure, split, or modernize `AGENTS.md` or the project's knowledge cache.
- **Vendor directory at the project root.** A `.kilo/`, `.claude/`, `.cursor/`, etc. directory is found — the skill guides unification under `.agents/<vendor>/`.

The skill covers: Phase 0 investigation (sourcing order, what to extract, prefer executable truth over prose), AGENTS.md detection (and ignoring vendor-specific agent files), README↔AGENTS.md separation, the standard project directory layout (`AGENTS.md`, `docs/`, `README.md`, `.agents/`, `.agents/docs/cache/`, `.tmp/`), vendor-directory unification with symlinks, `.kilo/rules/` and `.agents/kilo/skills/` integration, knowledge-cache conventions, writing rules (include/exclude), when to ask the user questions, and "when to suggest" timing.
