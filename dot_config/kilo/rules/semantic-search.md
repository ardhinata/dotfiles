# Semantic Search (`semantic_search`)

The `semantic_search` tool finds code by **meaning**, not exact text. It is low-cost, returns up to 16 results (min score 0.5), and should be used liberally.

## Usage Guidelines

### When to Use

- You are exploring an unfamiliar area of the codebase before knowing exact identifiers or file names
- You need to find related implementations of a concept (e.g., "authentication flow", "error handling middleware", "database connection pooling")
- You are searching by intent rather than by exact symbol or regex
- You want to narrow a large codebase before following up with `Grep` or `Read`
- Parallel discovery: launch `semantic_search` alongside `Grep` and `Glob` in the same batch to cover both meaning-based and pattern-based discovery simultaneously

### When to Avoid

- Searching for an exact symbol, string literal, or regex → use `Grep`
- Finding files by filename or extension → use `Glob`
- Reading the contents of a known file → use `Read`

### Query Best Practices

- Write queries in **natural English**
- Be specific about the concept or behavior you are looking for (e.g., "session cookie parsing" rather than "cookies")
- Limit scope with the `path` parameter when you know the relevant subdirectory
- Use the `path` parameter to constrain search to a single subdirectory; do not set it to the entire workspace unless necessary

### Handling Capped Results

When the result count reaches the max of 16 and none of the returned items are relevant:

1. **Retry with a more targeted query** — narrow the concept description, include specific terminology you've seen in the codebase
2. **Add a `path` constraint** — scope to a specific subdirectory instead of the full workspace
3. **Combine with `Grep` or `Glob`** — use those tools first to identify candidate files, then run `semantic_search` with the discovered path to find related code

### Parallel Usage Pattern

```markdown
To understand how feature X works:
1. `semantic_search` query: "feature X implementation details"   ← meaning-based discovery
2. `grep` pattern: "FeatureX\|feature_x\|featureXHandler"        ← exact symbol search
3. `glob` pattern: "**/feature-x*"                                ← file name search
All three run simultaneously in one batch.
```
