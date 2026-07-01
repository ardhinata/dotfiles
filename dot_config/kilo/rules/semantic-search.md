# Semantic Search (`semantic_search`)

`semantic_search` finds code by **meaning**, not exact text. Low-cost; returns up to 16 results (min score 0.5 — matches `kilo.jsonc` `searchMinScore`/`searchMaxResults`). Use liberally for exploration.

## When to Use vs Alternatives

- Exact symbol / string / regex → `grep`
- Filename / extension → `glob`
- Contents of a known file → `read`
- Exploring by intent before knowing identifiers, or finding related implementations → `semantic_search`

## Query Best Practices

- Natural English, specific to the concept (e.g. "session cookie parsing", not "cookies")
- Constrain with the `path` parameter to a known subdirectory; only drop `path` after scoped results come back empty

## Capped-Results Recovery

When results hit 16 and none are relevant:

1. Retry with a more targeted query — narrower concept, terminology you've seen in the codebase
2. Add a `path` constraint
3. Use `grep`/`glob` first to find candidate files, then `semantic_search` scoped to that path

## Parallel Discovery

Batch meaning-based and pattern-based discovery in one call:

```text
semantic_search: "feature X implementation details"
grep:           "FeatureX|feature_x|featureXHandler"
glob:           "**/feature-x*"
```

Prefer scoped queries first; widen only when scoped results are empty or off-topic.
