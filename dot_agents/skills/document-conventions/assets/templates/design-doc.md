# Design Doc Template

Copy to `docs/design/<slug>.md` in the project repo, or to
`docs/design/<slug>/` with `README.md` plus `NN-<section>.md` when the doc
passes its hard ceiling.

Modelled on [Software Engineering at Google, ch.10 — Documentation](https://abseil.io/resources/swe-book/html/ch10.html),
with the goals, non-goals and trade-off structure of the
[Kubernetes KEP template](https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md).

```markdown
---
status: <draft | review | accepted | implemented | abandoned>
last-updated: YYYY-MM-DD
---

# <Design title in sentence case>

<One paragraph. What this design covers and why it exists now.>

## Problem

<The problem in the reader's terms. What breaks today, who it breaks for,
and how often. State the evidence: a measurement, a report, a log.>

## Goals

- <what this design must achieve>

## Non-goals

- <what this design deliberately does not do, and why>

## Proposed design

<The design, in depth. Walk through the user-visible change first, then the
internals. Include the data model, the interfaces, and the flow.>

### Security, privacy, and data handling

<What the design stores, transmits, and authorizes. What an attacker can
reach, and what the design does about it.>

### Internationalization

<Locale, time zone, and text handling. Say "none needed" and say why.>

### Storage and migrations

<What is stored, where, and how an existing deployment migrates.>

### Trade-offs

<Each key decision, with the alternative rejected and why.>

## Alternatives considered

### <Alternative 1>

<One paragraph on why this was not chosen.>

### <Alternative 2>

<One paragraph on why this was not chosen.>

## Testing

<How the design is verified: unit, integration, load, or manual steps.>

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| <what can go wrong> | <low / medium / high> | <what limits the damage> |

## Open questions

- <question that must be answered before implementation>

## Related

- [<related ADR>](../adr/NNNN-<slug>.md)
- [<related RFC>](../rfcs/NNNN-<slug>.md)
```

**Length:** 500–2000 lines. Over the hard ceiling, split into a directory.

**Hard rules:**

- Goals AND non-goals. Non-goals are the part that gets dropped, and it
  decides the scope.
- Every alternative gets a one-paragraph dismissal.
- Security, privacy, internationalization, and storage are each answered.
  "Not applicable" is an answer. Silence is not.
- The design names the trade-off for each key decision.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
