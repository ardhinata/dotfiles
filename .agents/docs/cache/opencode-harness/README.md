# opencode-harness

Facts about how the OpenCode harness and its plugins behave: model routing,
session semantics, and plugin configuration limits.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-10-28 | [The ensemble model pool cannot carry a `#variant`](2026-10-28-ensemble-model-pool-variant.md) | `@hueyexe/opencode-ensemble@0.20.0`, OpenCode v2.1.4 source | check 2027-01 | `modelPool` is `string[]` and `parseModelId` splits at the first slash, so a `#variant` suffix stays inside the model id and fails the lookup. The teammate session lands on `variant = "default"`. |
