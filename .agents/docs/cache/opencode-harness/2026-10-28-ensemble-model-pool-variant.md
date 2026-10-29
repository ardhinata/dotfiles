---
source:
  - https://www.npmjs.com/package/@hueyexe/opencode-ensemble
captured: 2026-10-28
freshness: check-2027-01
tags: [opencode, ensemble, model-routing]
---

# The ensemble model pool cannot carry a `#variant`

A `#variant` suffix in an opencode-ensemble `modelPool` entry breaks the model
lookup instead of selecting the variant.

Captured 2026-10-28 while investigating why a `#medium` suffix in the
opencode-ensemble `modelPool` had no effect.

## Finding

The opencode-ensemble plugin cannot apply a reasoning variant to a teammate
model. A `#variant` suffix in a pool entry breaks the model lookup instead of
selecting the variant.

## Evidence

**The pool is a plain string list.** `modelPool` is `string[]`
(`src/config.ts:27` in `@hueyexe/opencode-ensemble@0.20.0`). The config parser
accepts it only when every element is a string (`src/config.ts:71`). Each entry
is rendered verbatim as a `question` option label
(`src/system-prompt.ts:104-105`).

**The parser splits at the first slash and keeps the rest as the model id.**
`parseModelId` (`src/member-model.ts:14-18`) returns
`{ providerID: model.slice(0, slash), modelID: model.slice(slash + 1) }`. The
model portion may contain further slashes, so
`openrouter/minimax/minimax-m3.1-flash` parses to the provider `openrouter` and
the model `minimax/minimax-m3.1-flash`. A `#variant` suffix stays inside the
model id, so `openrouter/minimax/minimax-m3.1-flash#high` parses to the model
`minimax/minimax-m3.1-flash#high`. That id does not exist, so the lookup fails.

**The spawn path passes only provider and model.** `team-spawn.ts:416` calls
`parseModelId(resolvedModel)` and logs a warning when the result is undefined.
`team-spawn.ts:427` spreads `{ model: modelParam }` into `promptAsync`.

**The V2 client drops the variant.** `src/v2-client.ts:216-219` calls
`ctx.session.switchModel` with `{ providerID, id: options.model.modelID }`.
The parsed object has no variant field, so none is sent.

**A session without an explicit variant falls back to `"default"`.**
`packages/core/src/session/info.ts:30` reads
`Model.VariantID.make(row.model.variant ?? "default")`. The `"default"` value
is neither the root `#high` pin in the config nor the model's own default
effort.

**Resolution order.** `resolveModel` (`src/tools/team-spawn.ts:19-33`) prefers
an explicit argument, then `modelsByAgent`, then the rotate or random pool,
then `defaultModel`. The priority comment sits at `src/tools/team-spawn.ts:18`.

**The HTTP API can carry a variant.** `session.create` takes an optional
`Model.Ref` (`packages/protocol/src/groups/session.ts:162`). `Model.Ref.parse`
(`packages/schema/src/model.ts:27-41`) splits the `#variant` suffix correctly.
The plugin never builds such a reference. An upstream patch is possible.
Version 0.20.0 has none.

## Why it matters

A teammate model that carries no variant runs at the harness default. Pinning
effort on a teammate therefore needs a different mechanism than the pool.

Two mechanisms work today:

- Set `agents.<agentName>.model` with a variant in `opencode.jsonc`. A
  session-level model wins over an agent-level one, so pass no model at spawn.
  The agent-level path runs when the session has no model
  (`packages/core/src/session/runner/model.ts:79-90`).
- Let the plugin's `defaultModel` carry the variant. It reaches the same
  `parseModelId` path, so a `#` suffix fails there too.

## Scope

opencode-ensemble 0.20.0 and OpenCode v2.1.4. The plugin pins the model at
spawn time and never revisits it, so a later config change does not move a
running teammate.

## Uncertainty

The upstream fix is not published. The plugin authors may add a variant field
to `ParsedModel` in a later release. Re-verify after any plugin upgrade.

## Sources

- `@hueyexe/opencode-ensemble@0.20.0` (`src/member-model.ts:14-18`,
  `src/v2-client.ts:216-219`, `src/tools/team-spawn.ts:19-33`).
- OpenCode v2.1.4 (`packages/core/src/session/info.ts:30`,
  `packages/protocol/src/groups/session.ts:162`,
  `packages/schema/src/model.ts:27-41`).

## See also

- `docs/plans/2026-10-28-research-loop-instruction-fixes.md` — the plan that
  produced this entry
- `docs/post-mortem/2026-10-28-overlong-variant-research-loop.md` — the
  incident that made this fact worth caching
