# opencode-harness

Facts about how the OpenCode harness and its plugins behave: model routing,
session semantics, and plugin configuration limits.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-10-28 | [The ensemble model pool cannot carry a `#variant`](2026-10-28-ensemble-model-pool-variant.md) | `@hueyexe/opencode-ensemble@0.20.0`, OpenCode v2.1.4 source | check 2027-01 | `modelPool` is `string[]` and `parseModelId` splits at the first slash, so a `#variant` suffix stays inside the model id and fails the lookup. The teammate session lands on `variant = "default"`. |
| 2026-10-29 | [OpenCode 2.2.1 drops every AFT tool](2026-10-29-opencode-2-2-1-zod-tool-registration.md) | `@opencode/cli` 2.2.0 and 2.2.1, `@cortexkit/aft-opencode@0.62.0`, `zod` 4.1.8 to 4.6.7 | check 2027-01 | The 2.2.1 binary ships zod 4.6.7. zod 4.3.0 and later throw a TypeError when a schema has both a custom `_zod.toJSONSchema` override and a `_zod.parent`, which is the shape that AFT registers. opencode skips each tool and logs `Skipping invalid tool registration`. opencode 2.2.0 is unaffected. |
