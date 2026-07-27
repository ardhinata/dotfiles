# Transient Plan Template

Copy to `.tmp/plans/<task-slug>-YYYY-MM-DD.md`. Per the
`personal-quirks` planning rule. **Pre-planning duplicate scan is
mandatory.**

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

**Filename:** `<task-slug>-YYYY-MM-DD.md`. Lowercase + hyphens. No
collisions — pre-create scan mandated by `personal-quirks.md`.

**Update cadence:** at every checkpoint / milestone. Don't let the file
drift from reality.

**Verification:** manual review against [`../checklists.md`](../checklists.md)
and `~/.config/kilo/rules/personal-quirks.md`.