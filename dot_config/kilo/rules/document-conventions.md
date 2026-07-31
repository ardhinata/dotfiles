# Document Conventions Router

Router rule. Triggers load the `document-conventions` skill on demand.

## Load the `document-conventions` skill eagerly when any of these is true

- **About to author or edit any doc type.** A new note, plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, Kilo rule, or skill is being drafted.
- **Validating a filename or frontmatter.** Confirming a name follows the kebab-case / ISO 8601 / date-first rules; checking whether frontmatter is required, forbidden, or optional for the type.
- **Choosing between doc types.** The decision matrix is the authoritative picker.
- **Reviewing an existing document.** Confirming section order, length budget, and structure match the per-type policy.
- **Aligning to project or open-spec rules.** Adapting structure to the agents.md open spec, agentskills.io spec, MADR ADR format, Keep a Changelog 1.1.0, Conventional Commits 1.0.0, etc.

## Boundary with neighbouring skills

- **Per-doc-type shape** (filename, frontmatter, section order, length budget, decision matrix, templates) → `document-conventions` (this rule).
- **Where a file lives in a project tree** (canonical paths, `.tmp/` subroles, vendor path unification, knowledge-cache placement) → `project-layout` (load via the `project-context` rule).
- **AGENTS.md lifecycle** (detection, README↔AGENTS separation, vendoring trigger, rules/skills integration) → `project-context` (load via the `project-context` rule).

Do not modify these skill descriptions to overlap. If a question spans two concerns, load both skills.