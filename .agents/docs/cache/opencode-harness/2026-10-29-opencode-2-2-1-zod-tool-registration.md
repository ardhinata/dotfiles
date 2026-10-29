---
source:
  - https://www.npmjs.com/package/@opencode/cli
  - https://www.npmjs.com/package/@cortexkit/aft-opencode
  - https://www.npmjs.com/package/zod
captured: 2026-10-29
freshness: check-2027-01
tags: [opencode, aft, zod, tool-registration]
---

# OpenCode 2.2.1 drops every AFT tool

OpenCode 2.2.1 refuses every tool that the AFT plugin registers. The server
log shows one `Skipping invalid tool registration` error per tool. The agent
then runs without file and shell tools.

Captured 2026-10-29. The source was a log from the Mac machine, where the
opencode CLI updated itself from 2.2.0 to 2.2.1.

## Finding

The failure comes from a version change inside the opencode binary. The
binary ships zod 4.6.7 in 2.2.1 and zod 4.1.8 in 2.2.0. The AFT plugin
builds schemas for tools that zod 4.6.7 cannot convert. opencode catches the
conversion error for each tool and skips the tool. The session then starts
without the AFT tools.

## Evidence

**The error text points at zod.** Each line names the step that fails.

```text
message="Skipping invalid tool registration" name=read
  error="Invalid tool definition read: undefined is not an object (evaluating 'a.ref')"
```

Bun reports the same TypeError as `Cannot read properties of undefined
(reading 'ref')`.

**opencode 2.2.1 ships zod 4.6.7.** The root `package.json` catalog lists
`"zod": "4.6.7"`. The same file in tag `v2.2.0` lists `"zod": "4.1.8"`.

**zod 4.6.7 drops the parent of a schema that has a custom JSON Schema
override.** `processSchema` (`zod/v4/core/to-json-schema.js:83`) reads the
custom method `schema._zod.toJSONSchema`. When the method exists, the code
skips the branch that registers the parent schema and sets `result.ref`
(lines 104 to 108). `flattenRef` later recurses into that parent without a
lookup check (line 444) and reads `seen.ref` of an undefined entry
(line 397). The result is the TypeError.

**The bug starts at zod 4.3.0.** A standalone test converts a zod 4.1.8
schema with the custom override and a `.describe()` parent. zod 4.1.8 and
4.2.0 convert the schema. zod 4.3.0 up to 4.6.7 throw the TypeError.

**AFT creates exactly that schema.** `attachJsonSchemaOverride`
(`dist/entry/server.js:43923` in `@cortexkit/aft-opencode@0.62.0`) installs
a custom `_zod.toJSONSchema` on every argument schema.
`renameArgumentDescriptions` (line 46011) calls `.describe()` on the
arguments. In zod v4, `.describe()` returns a clone that keeps a link to the
original schema as `_zod.parent`. `projectV2Tool` (line 46104) joins the
arguments with `tool.schema.object(...)` and passes the result to the host.

**opencode converts the plugin schema with its own zod.**
`packages/core/src/tool/runtime.ts:170` calls `toJSONSchema(schema, { target:
"draft-2020-12", io })` from the host copy of zod. The `register` function in
`packages/core/src/tool.ts:338` catches the TypeError and returns
`Invalid tool definition <id>: <message>`. The `notify` function in the same
file (line 230) writes the log line.

**The plugin list decides the outcome.** A test with opencode 2.2.1 and an
isolated `HOME` produced these results.

| Configuration | Registration errors |
|---|---|
| AFT only | 40 |
| AFT plus cc-safety-net, magic-context, handoff, ponytail, ensemble | 40 |
| Each of the other five plugins alone | 0 |
| opencode 2.2.0 plus AFT | 0 |
| opencode 2.2.1 plus AFT, with the custom override disabled | 0 |

## Why it matters

The failure is silent in the user interface. The server starts, the session
starts, and the model receives a tool list without the AFT tools. A later
tool call then fails with `No tool named "bash" is currently available`.

A machine that updates the opencode CLI on its own loses the file and shell
tools of the AFT plugin. The dotfiles pin the plugin as
`@cortexkit/aft-opencode@latest`, so the failure arrives with the next CLI
update.

## Scope

opencode 2.2.1, zod 4.6.7, and `@cortexkit/aft-opencode` 0.62.0. Every tool
works on opencode 2.2.0 because that release ships zod 4.1.8. No release of
zod above 4.6.7 and no release of AFT above 0.62.0 exists at the capture date.

## Uncertainty

The zod maintainers may add the lookup check. The AFT maintainers may
remove the custom override. The opencode maintainers may convert
plugin schemas with the plugin copy of zod. Until one of the three changes,
the downgrade stays in place.

## Sources

- `@opencode/cli` 2.2.0 and 2.2.1 (`package.json` catalog, `packages/core/src/tool.ts`,
  `packages/core/src/tool/runtime.ts`).
- `@cortexkit/aft-opencode` 0.62.0 (`dist/entry/server.js`).
- `zod` 4.1.8, 4.2.0, 4.3.0, 4.4.3, 4.5.4, 4.6.0, 4.6.5, 4.6.6, 4.6.7
  (`v4/core/to-json-schema.js`).

## See also

- `docs/post-mortem/2026-10-29-opencode-2-2-1-aft-tool-registration.md` — the
  incident that made this fact worth caching
