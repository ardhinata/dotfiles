# Document Conventions Router

Router rule. Triggers load the `document-conventions` skill on demand.

## Load the `document-conventions` skill eagerly when any of these is true

- **About to author or edit any doc type.** A new plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, rule, or skill is being drafted.
- **Validating a filename or frontmatter.** Confirming a name follows the kebab-case / ISO 8601 / date-first rules; checking whether frontmatter is required, forbidden, or optional for the type.
- **Choosing between doc types.** The decision matrix is the authoritative picker — load the skill rather than guessing.
- **Reviewing an existing document.** Confirming section order, length budget, and structure match the per-type policy.
- **Splitting a doc that outgrew its file.** A doc over its hard ceiling becomes a directory: an index `README.md` plus numbered section files `NN-<section-slug>.md`. The directory name is the slug the single file would have had.
- **Aligning to project or open-spec rules.** Adapting structure to the agents.md open spec, agentskills.io spec, MADR ADR format, Keep a Changelog 1.1.0, Conventional Commits 1.0.0, etc.

## Inline doc-type picker (preview)

Short form for the common cases. Load the skill for the full matrix when the type is ambiguous.

| If you need to capture… | Use | Lives at |
|---|---|---|
| A verified, reusable fact | knowledge-cache entry | `.agents/docs/cache/<topic>/<date>-<slug>.md` |
| A multi-step task in progress | persistent plan | `docs/plans/<date>-<task-slug>.md` |
| An architecture / tooling decision with rationale | ADR | `docs/adr/NNNN-<slug>.md` |
| Repo-wide convention, agent guidance, behaviour | rule | `~/.agents/rules/<slug>.md` (shared) or `~/.agents/rules.personal.d/<slug>.md` (personal) |
| Project knowledge for agents | AGENTS.md / SKILL.md | `AGENTS.md`, `.agents/skills/<name>/SKILL.md` |

## Boundary with neighbouring skills

Tree placement → `project-layout`; AGENTS.md lifecycle → `project-context` (full three-way split in `project-context.md`).