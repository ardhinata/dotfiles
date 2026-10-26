# Document Conventions Router

Router rule. Triggers load the `document-conventions` skill on demand.

## Load the `document-conventions` skill eagerly when any of these is true

- **About to author or edit any doc type.** A new plan, ADR, RFC, README,
  CHANGELOG, knowledge-cache entry, rule, or skill is being drafted.
- **Validating a filename or frontmatter.** Confirming a name follows the
  kebab-case, ISO 8601, and date-first rules, and checking whether frontmatter
  is required, forbidden, or optional for the type.
- **Choosing between doc types.** The decision matrix in the skill is the
  authoritative picker. Load the skill rather than guessing.
- **Reviewing an existing document.** Confirming section order, length budget,
  and structure match the per-type policy.
- **Aligning to project or open-spec rules.** Adapting structure to the
  agents.md open spec, the agentskills.io spec, MADR ADR format, Keep a
  Changelog 1.1.0, and Conventional Commits 1.0.0.

## Boundary with neighbouring skills

Tree placement → `project-layout`. AGENTS.md lifecycle → `project-context`.
