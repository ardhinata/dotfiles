# Local First, Don't Assume

When the user asks something, read the project's readily-available docs **before assuming or searching the web**. (Filename is `local-first`, not an ordering guarantee — `instructions: [".../*.md"]` loads as an unordered glob. The name just signals the behavior: prefer local sources first.) Do this on the first turn, not after guessing.

## Priority

In roughly this order — read what exists, skip what doesn't:

1. **`README.md`** — setup, intent, structure, conventions in one pass. Always skim early.
2. **Agent-instruction files** — `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.cursor/rules/`, `.github/copilot-instructions.md`. These are written *for agents*; they tell you how to behave here, not just what the project is.
3. **Executable manifests** — `package.json` (`scripts` block), `Cargo.toml`, `go.mod`, `pyproject.toml`, `composer.json`. The `scripts`/`tasks` section is executable truth about how the team builds/tests — it cannot drift like prose.
4. **Task runners** — `Makefile`, `Taskfile.yml`, `justfile`. Canonical commands the team actually runs.
5. **`CONTRIBUTING.md`** — workflow, branch/PR rules, style, test requirements.
6. **`CHANGELOG.md` / `RELEASES.md`** — recent behavior, deprecations, breaking changes. Critical when your knowledge cutoff predates the latest release.
7. **`.env.example` / `.env.template`** — required env vars (no secrets exposed). Check before assuming defaults.
8. **`docs/` index** — skim filenames/titles only, not contents. Tells you where deeper knowledge lives so you can target a single file later.
9. **Code itself** — when the above don't cover it, read the relevant source/config.

## When

- On the **first turn** of any project-scoped question — before searching the web or asking the user.
- Before `tavily_search`, `firecrawl_*`, or `context7` — the answer is usually local and more authoritative.
- Before a clarifying question the docs may already answer.

## Heuristic

Prefer **executable truth over prose**: manifests and task runners beat README paragraphs about "how to build". Prefer **agent-instruction files over general docs**: they're written for you. Prefer **recent (`CHANGELOG`) over comprehensive** when your cutoff is stale.

## Anti-Patterns

- Assuming project structure/conventions from filenames alone.
- Jumping to web search for a question the project's own docs resolve.
- Asking the user something stated in `README.md` or `AGENTS.md`.
- Reading `docs/` end-to-end upfront — skim the index, target one file when needed.
- Trusting a README's "how to build" over the actual `package.json` scripts when they disagree.
