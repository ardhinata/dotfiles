# Knowledge-Cache Entry Template

Copy to `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md`. Update the
topic's `README.md` (and the cache root `README.md` if the topic is
new).

```markdown
---
source: <URL of the original, with capture date>
captured: YYYY-MM-DD
freshness: <stable | check-YYYY-MM | volatile>
tags: [<tag-1>, <tag-2>]
---

# <Finding summary in sentence case>

<one-line summary>

## Finding

<The verified finding. One to three sentences. Plain language.>

## Evidence

<Exact file paths, command outputs, URLs, or code locations that
justify the finding. Quote sparingly.>

## Why it matters

<Which future decision or behavior this changes.>

## Scope

<Repo, machine profile, language/runtime, condition (e.g. `if podman`,
`if Docker shim`).>

## Uncertainty

<What is still unverified, what would re-validate this.>

## See also

- [related entry](./YYYY-MM-DD-other-slug.md)
- [external source](https://…)
```

**Length:** 30–150 lines.

**Filename:**

- ISO date prefix: `YYYY-MM-DD`
- Lowercase + hyphens slug
- Same-day collisions: append `-2`, `-3`, etc.

**Hard rules:**

- No secrets (tokens, keys, fingerprints, passwords)
- Always capture `source` and `captured`
- `freshness` field is required for cache usability

**Verification:** manual review against [`../checklists.md`](../checklists.md).
Index updated.