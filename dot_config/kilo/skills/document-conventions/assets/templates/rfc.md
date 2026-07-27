# RFC Template

Copy to `docs/rfcs/NNNN-<slug>.md`. Heavier than an ADR; for design
proposals that need formal review.

```markdown
---
status: <draft | review | accepted | rejected | withdrawn>
reviewers: [<handle>, <handle>]
deadline: YYYY-MM-DD
last-updated: YYYY-MM-DD
---

# <Slug title in sentence case>

## Summary

<One paragraph. The change and why it matters.>

## Motivation

<Why this change is needed. What problem it solves. Force-multiplied
data, user reports, prior art.>

## Detailed design

<The proposal, in depth. Walk through the user-visible change. Code,
diagrams, sequence flows as needed.>

## Drawbacks

<Why this might be the wrong choice. State them honestly.>

## Alternatives

<Each alternative gets a one-paragraph dismissal.>

### <Alternative 1>

<Why not.>

### <Alternative 2>

<Why not.>

## Open questions

- <question 1>
- <question 2>

## Unresolved questions

<Things the team must decide before this RFC can be accepted.>

## Prior art

<What other projects did similar work. Links.>

## Future possibilities

<What this enables, beyond the immediate change.>

## Implementation plan

<Optional. Step-by-step rollout. Link to a persistent plan if the
rollout is large.>

## Acknowledgements

<Optional.>
```

**Length:** 200–1000 lines target; up to 2000 for heavyweight
proposals.

**Filename:** `NNNN-<slug>.md`. 4-digit zero-padded, append-only.

**Status values:** `draft` → `review` → `accepted` / `rejected` /
`withdrawn`.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
Confirm reviewers + deadline are filled before requesting review.