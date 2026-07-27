# Kilo Rule Template

Copy to `dot_config/kilo/rules/<slug>.md`. **No frontmatter** — this is
a project-wide decision (see [`references/frontmatter.md`](../../references/frontmatter.md)).
Kilo's loader does not parse YAML, so any frontmatter here is dead
weight that drifts.

```markdown
# <Rule summary in sentence case>

<one-line description, no heading>

## When

<Trigger / "When" header. State the conditions that activate this
rule.>

## <Rule body>

<The rule itself. Concise. Prefer bullets over prose. Reference
related rules, skills, or files rather than restating.>

## Anti-patterns

- <common mistake 1>
- <common mistake 2>

## References

- <link 1>
- <link 2>
```

**Length:** 30–80 lines target; 150 hard ceiling. If longer, split into
multiple rules or push detail to a skill.

**Slug rules:** lowercase, hyphens, no trailing punctuation. Match the
intent, not the filename (e.g. `fnm.md` not `node-version-management.md`).

**Verification:** no frontmatter parser exists; review by hand against
the [`checklists.md`](../checklists.md).