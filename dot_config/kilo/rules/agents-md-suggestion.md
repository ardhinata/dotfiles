# AGENTS.md Suggestion

When starting work in a project that does not have an `AGENTS.md` (or `CLAUDE.md` / `CONTEXT.md`) at the workspace root, suggest to the user that they create one.

## Why

`AGENTS.md` is auto-loaded into every conversation as system instructions. A concise project-level file reduces the need for the user to repeat project context, conventions, and constraints in every prompt.

## What to Include

A good `AGENTS.md` is short (10-30 lines) and covers:

- Project purpose and tech stack (1-2 sentences)
- Key conventions the agent should follow (3-5 bullet points)
- Commands for testing, linting, building
- Pointers to detailed docs/rules (e.g., `docs/CONTRIBUTING.md`, `.kilo/rules/`)

## When to Suggest

Suggest it when:
- The user repeats the same project context across multiple conversations
- The project has complex conventions that aren't obvious from the directory structure
- You spend more than 2 turns explaining project-specific patterns

Keep the suggestion brief: "This project doesn't have an `AGENTS.md`. Creating one would help me remember <key conventions> across sessions. Want me to draft one?"
