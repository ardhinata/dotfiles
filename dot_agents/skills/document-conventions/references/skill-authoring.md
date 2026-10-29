# Skill Authoring

How to write a skill that earns its context budget. The file format — the
frontmatter fields, the length budget, the validation command — is specified
in [`by-doc-type.md`](by-doc-type.md). This file covers the craft.

## Start from real expertise

Do not ask a language model to generate a skill from its training knowledge.
Feed it domain-specific context instead. Extract that context from:

- **Completed tasks.** The steps that worked, the corrections you made, the
  context you had to supply.
- **Existing artifacts.** Internal docs, API specs, code review comments,
  patch history, real failure cases.

## Spend context wisely

Every token competes for attention. **Add what the agent lacks. Omit what it
already knows.** You do not need to explain what a PDF is or how HTTP works.
Skip generic advice such as "handle errors appropriately". Include the
concrete corrections to mistakes the agent will make.

The specification loads a skill in three layers. Write for the layer the text
belongs to.

| Layer | Size | Loaded |
|---|---|---|
| Metadata | about 100 tokens | At startup, for every skill |
| Instructions | under 5000 tokens | When the skill activates |
| Resources | as needed | Only when the agent reads the file |

So the `name` and `description` are the only words every agent pays for. The
body is paid for once, when the skill activates. Anything beyond that should
sit in `references/` or `scripts/`, behind a stated trigger.

## Match specificity to fragility

- **Give freedom** when several approaches work. Explain *why*, not only *what*.
- **Be prescriptive** when the operation is fragile or the order matters.
  Give the exact command and the exact flags.
- **Give a default, not a menu.** Pick one tool. Name the alternatives as
  fallbacks, not as equal options.

## Favor procedures over declarations

Teach *how to approach* a problem class, not *what to produce* for one
instance. A reusable method beats a specific answer.

## Effective patterns

| Pattern | When to use it |
|---|---|
| **Gotchas section** | Facts that defy a reasonable assumption: naming mismatches, soft deletes, misleading health endpoints |
| **Output templates** | When the output must follow a fixed format. A template beats a prose description |
| **Checklists** | Multi-step work with dependencies or validation gates |
| **Validation loops** | The agent validates its own work before proceeding: run the validator, fix, repeat |
| **Plan, validate, execute** | Batch or destructive operations. Build a plan, check it against the source of truth, then run it |
| **Bundled scripts** | When agents repeatedly reinvent the same logic across runs |

## Iterate with real execution

Run the skill against real tasks. Read the agent's execution traces, not
only its final output. Feed what you find back into the gotchas section. One
pass of execute-then-revise improves the skill noticeably.

## Validate

```bash
skills-ref validate ./<skill-dir>
```

The command checks the frontmatter and the naming rules. When it is not on
PATH, review by hand: the frontmatter fields are present, the `name` matches
the directory name, and the `description` names both *what* the skill does
and *when* to use it.

## References

- [agentskills.io specification](https://agentskills.io/specification) — the
  format itself.
- [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Equipping agents for the real world with agent skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
