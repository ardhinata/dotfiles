# Document Conventions Router

Router rule. Triggers load the `document-conventions` skill on demand.

## Load the `document-conventions` skill eagerly when any of these is true

- About to author or edit any doc type.
- Choosing between doc types — use the skill's decision matrix, never a guess.
- A filename, frontmatter, or structure review is on the table. The skill owns
  the naming rules, the frontmatter policy, and the section order.
- Aligning a document to a project or open-spec rule — the agents.md open
  spec, the agentskills.io spec, MADR, Keep a Changelog, or Conventional
  Commits.

## Boundary with neighbouring skills

Tree placement → `project-layout`. AGENTS.md lifecycle → `project-context`.
Prose clarity → `asd-ste100`.
