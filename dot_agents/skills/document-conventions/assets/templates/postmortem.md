# Postmortem Template

Copy to `docs/post-mortem/YYYY-MM-DD-<slug>.md` in the project repo.
Plain Markdown — no frontmatter is required, but the metadata block below is
recommended.

Modelled on [Google SRE — Example Postmortem](https://sre.google/sre-book/example-postmortem/),
with the owner, severity and responder fields from the
[PagerDuty postmortem template](https://response.pagerduty.com/after/post_mortem_template/).

**Blameless.** The postmortem names contributing causes, never a person or
team as the cause. "Human error" is a starting point, not a conclusion. See
[Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/).

```markdown
---
severity: <SEV-1 | SEV-2 | SEV-3 | SEV-4>
status: <draft | review | complete>
date: YYYY-MM-DD
owner: <who owns the follow-up>
---

# <Incident title in sentence case>

<One paragraph. What broke, who noticed, what the effect was, and what
changed as a result.>

## Summary

<What happened, in two or three sentences. A reader who stops here must
know the incident, the impact, and the outcome.>

## Impact

<Duration, who was affected, how many requests or users, and the effect on
revenue or data. Numbers, not adjectives.>

## Root cause

<The contributing causes, most significant first. Each cause links to the
part of the system that produced it. Name no individual.>

## Trigger

<The change, event, or condition that turned the underlying fault into a
visible incident.>

## Detection

<How the incident was noticed: alert, user report, or manual discovery.
State how long detection took.>

## Resolution

<What was done to restore service, and when. State any mitigation that
failed and any workaround that was applied.>

## Timeline

| Time (UTC) | Event |
|---|---|
| YYYY-MM-DD HH:MM | <what happened> |
| YYYY-MM-DD HH:MM | <what happened> |

<Responders, if useful: who took part in the response.>

## Lessons learned

- <What went well>
- <What went poorly>
- <What we got lucky about>

## Action items

| Action item | Type | Priority | Owner | Tracking issue |
|---|---|---|---|---|
| <what must change> | <prevent / detect / mitigate / other> | <P0–P3> | <who> | <issue link> |

Every action item has an owner, a priority, and a tracking issue. An
action item without a tracking issue does not exist.
```

**Length:** 50–300 lines.

**Filename:** `YYYY-MM-DD-<slug>.md`. The date is the incident date, not
the write date.

**Hard rules:**

- Blameless. Name systems, not people.
- Every action item carries an owner, a priority, and a tracking issue.
- The postmortem has one owner for the follow-up.
- Impact is measured, not described.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
