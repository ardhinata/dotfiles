# Persistent Plan Template

Copy to `docs/plans/YYYY-MM-DD-<task-slug>.md` in the project repo
(or to a user-specified path). Persistent plans live in the project repo
and are committed with it. Update the file in place at every checkpoint.

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

<Findings that could not be captured yet. One line each, with enough
context to act later.>

## Current status

<Last-updated checkpoint. Concise.>
```

**Length:** < 300 lines target, 500 hard ceiling. Split into phases
if longer.

**Filename:** `YYYY-MM-DD-<task-slug>.md`. Lowercase + hyphens. Scan the
target directory before writing to avoid a same-day slug collision.

**Update cadence:** at every checkpoint / milestone. Do not let the file
drift from reality.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
