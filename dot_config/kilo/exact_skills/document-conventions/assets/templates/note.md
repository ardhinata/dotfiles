# Note Template

Copy to `.tmp/docs/notes/YYYY-MM-DD-<task-slug>.md`. Per the
`proactive-note-capture` rule, the section order below is **mandatory**.
After writing, run `kilo-shared save "<short-message>"` to commit the
note to the shared context repo. See the `shared-context` skill.

```markdown
---
task: <task-slug>
status: <open | captured | promoted>
captured: YYYY-MM-DD
---

# <Finding summary in sentence case>

## Finding

<The verified finding. One to two sentences.>

## Evidence

<Exact file paths, command outputs, URLs, or code locations.>

## Why it matters

<Which future decision or behavior this changes.>

## Scope

<Repo, machine profile, language/runtime, condition.>

## Uncertainty

<What is still unverified, what would re-validate this.>

## Recommended destination

<Where this should eventually live: a rule file, a skill, an ADR,
etc.>

## Date captured

YYYY-MM-DD

## Next action

<Optional: what to do with this finding next.>

## See also

- [related note](./YYYY-MM-DD-other-note.md)
- [related plan](../../plans/YYYY-MM-DD-plan.md)
```

**Length:** < 150 lines.

**Filename:** `YYYY-MM-DD-<task-slug>.md`. Lowercase + hyphens. Avoid
collisions with a pre-create scan (the rule mandates this).

**Hard rules:**

- No secrets, tokens, keys, fingerprints, passwords, recovery phrases
- All seven mandatory sections present
- ISO date in `## Date captured` and in the filename
- `## Recommended destination` must be filled — even with "discard"

**Verification:** manual review against [`../checklists.md`](../checklists.md)
and `~/.config/kilo/rules/proactive-note-capture.md`.