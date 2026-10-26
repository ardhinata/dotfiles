# Project Context Router

Router rule. Triggers load the `project-context` and `project-layout` skills
together.

## Load both eagerly when any of these is true

- The project has no `AGENTS.md`.
- The user asks to create, update, split, or modernize `AGENTS.md`.
- A vendor directory sits at the project root and is not already a symlink
  into `.agents/<vendor>/`.
- The question is about where a file lives in the project tree.

## Load one alone

- `project-context` alone: AGENTS.md content, README and AGENTS.md separation,
  and the vendoring trigger.
- `project-layout` alone: tree placement, vendor path mechanics, and cache
  path migration.

Do not let the two skill descriptions overlap. If a question fits both
concerns, load both.
