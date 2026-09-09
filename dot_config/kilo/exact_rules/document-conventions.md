# Document Conventions Router

Router rule. Triggers load the `document-conventions` skill on demand.

## Load the `document-conventions` skill eagerly when any of these is true

- **About to author or edit any doc type.** A new note, plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, Kilo rule, or skill is being drafted.
- **Validating a filename or frontmatter.** Confirming a name follows the kebab-case / ISO 8601 / date-first rules; checking whether frontmatter is required, forbidden, or optional for the type.
- **Choosing between doc types.** The decision matrix is the authoritative picker — load the skill rather than guessing.
- **Reviewing an existing document.** Confirming section order, length budget, and structure match the per-type policy.
- **Aligning to project or open-spec rules.** Adapting structure to the agents.md open spec, agentskills.io spec, MADR ADR format, Keep a Changelog 1.1.0, Conventional Commits 1.0.0, etc.

## Inline doc-type picker (preview)

Short form for the common cases. Load the skill for the full matrix when the type is ambiguous.

| If you need to capture… | Use | Lives at |
|---|---|---|
| A verified, reusable fact from a web lookup | knowledge-cache entry | `.agents/docs/cache/<topic>/<date>-<slug>.md` |
| A task-only finding for the active work | note (immediate) | `.tmp/docs/notes/<date>-<task-slug>.md` |
| A multi-step task in progress | plan | `.tmp/docs/plans/<date>-<task-slug>.md` |
| An architecture / tooling decision with rationale | ADR | `docs/decisions/NNNN-<slug>.md` |
| Repo-wide convention, agent guidance, behaviour | rule | `dot_config/kilo/exact_rules{,*.personal.d}/<slug>.md` |
| Project knowledge for agents | AGENTS.md / SKILL.md | `AGENTS.md`, `.agents/kilo/skills/<name>/SKILL.md` |

## Boundary with neighbouring skills

Tree placement → `project-layout`; AGENTS.md lifecycle → `project-context` (full three-way split in `project-context.md`).