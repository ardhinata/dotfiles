# Report Template

Copy to `docs/reports/<YYYY-MM-DD>-<slug>.md`. A report is something you hand
to another person. Write it so they can act on it without asking you a
question.

```markdown
---
status: <draft | open | fixed>
severity: <blocker | major | minor>
---

# <One line: what is wrong>

## Summary

<What happens, in two or three sentences. The reader should know whether this
is the bug they were told about.>

## Steps to reproduce

1. <start from a known state>
2. <the action that triggers it>
3. <the action that shows the problem>

## Expected

<What should have happened.>

## Actual

<What happened instead. Paste the exact error text.>

## Environment

<Version, operating system, configuration. Only the parts that matter.>

## Impact

<Who is blocked, how badly, and since when.>

## Workaround

<How to live with it until it is fixed. Write "None" when there is none.>

## Suspected cause

<Your best guess, with the evidence for it. Mark it a guess.>

## Related

- <links to issues, plans and other reports>
```

**Before you send it:**

- Another person can reproduce the problem from this file alone.
- The error text is exact, not paraphrased.
- The version is the one that shows the problem.
- Every claim about the cause is marked as a guess or as verified.

**Not a postmortem.** A postmortem looks back at a closed incident and carries
an owner and a tracking issue for every action item. A report describes
something that still needs attention. Write the report first, and point at it
from the postmortem if the incident later gets one.
