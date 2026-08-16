# ADR Template (MADR)

Copy to `docs/adr/NNNN-<slug>.md`. Frontmatter is optional but
recommended. Sections in **MADR order** (fixed).

```markdown
---
status: "<proposed | rejected | accepted | deprecated | superseded by ADR-NNNN>"
date: YYYY-MM-DD
decision-makers: [<handle>, <handle>]
consulted: [<handle>]
informed: [<team>]
---

# <Short title of the solved problem and chosen solution>

## Context and Problem Statement

<Describe the context and problem statement in two to three sentences
or as an illustrative story. Articulate the problem as a question
when useful.>

<!-- optional -->
## Decision Drivers

- <driver 1>
- <driver 2>

## Considered Options

- <option 1>
- <option 2>
- <option 3>

## Decision Outcome

Chosen option: "<option 1>", because <justification>.

<!-- optional -->
### Consequences

* Good, because <positive consequence>
* Bad, because <negative consequence>
* Neutral, because <…>

<!-- optional -->
### Confirmation

<How implementation will be verified — design review, test, metric,
etc.>

<!-- optional -->
## Pros and Cons of the Options

### <option 1>

* Good, because <argument>
* Bad, because <argument>

### <option 2>

* Good, because <argument>
* Bad, because <argument>

<!-- optional -->
## More Information

<Additional evidence, links to other ADRs, when to re-visit.>
```

**Length:** 50–200 lines.

**Filename:** `NNNN-<slug>.md`. NNNN is 4-digit zero-padded. Sequence
is append-only; do not renumber.

**Status values:** `proposed` / `rejected` / `accepted` / `deprecated`
/ `superseded by ADR-NNNN`. Update; never delete.

**No numbering in headings** (MADR ADR-0002). The number is in the
filename, not the H1.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
Run a sequence check (`ls docs/adr/`) to confirm no gaps if you renumber.