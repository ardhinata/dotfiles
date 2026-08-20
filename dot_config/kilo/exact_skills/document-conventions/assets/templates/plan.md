# Plan Template

Copy to `.tmp/docs/plans/YYYY-MM-DD-<task-slug>.md`. Per the planning
rule (`~/.config/kilo/rules/plans.md`). **Pre-planning duplicate scan
is mandatory** — `kilo-shared pull origin main` plus a local `ls`.
After each checkpoint, run
`kilo-shared save "checkpoint: <one-line>"`. See the
`shared-context` skill.

```markdown
---
status: <draft | active | completed | abandoned>
goal: <one-line goal>
owner: <who>
last-updated: YYYY-MM-DD
---

# <Task summary in sentence case>

## Goal

<What this plan achieves. One paragraph.>

## Scope

- In: <what this plan covers>
- Out: <what this plan does not cover>

## Existing constraints

<Rules, files, decisions that bound this plan.>

## Refined approach

<The strategy, not just the steps. Why this approach.>

## Implementation steps

1. <step 1>
2. <step 2>
3. <step 3>

## Risks and mitigations

- Risk: <…>. Mitigation: <…>.
- Risk: <…>. Mitigation: <…>.

## Open questions

- <question 1>
- <question 2>

## Decisions

- <date>: <decision and reason>

## Deferred notes

<Per the proactive-note-capture rule: when capture is blocked, list
findings here with enough context to act later.>

## Current status

<Last-updated checkpoint. Concise.>
```

**Length:** < 300 lines target; 500 hard ceiling. Split into phases
if longer.

**Filename:** `YYYY-MM-DD-<task-slug>.md`. Lowercase + hyphens. No
collisions — pre-create scan mandated by `~/.config/kilo/rules/plans.md`.

**Update cadence:** at every checkpoint / milestone. Don't let the file
drift from reality.

**Verification:** manual review against [`../checklists.md`](../checklists.md)
and `~/.config/kilo/rules/plans.md`.