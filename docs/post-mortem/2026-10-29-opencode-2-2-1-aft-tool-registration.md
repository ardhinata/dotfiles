---
severity: high
status: open
date: 2026-10-29
---

# OpenCode 2.2.1 drops every AFT tool — post-mortem

## Summary

The Mac machine updated the opencode CLI from 2.2.0 to 2.2.1 on
2026-10-29. After the update, the agent lost all 20 tools that the AFT plugin
registers. The tools were `read`, `write`, `edit`, `patch`, `shell`,
`grep`, `glob`, the four `bash_*` tools, the eight `aft_*` tools, and the two
`ast_grep_*` tools. Twenty tools in total.

The failure produced no message in the user interface. The server started,
the session started, and the model received a tool list without the AFT
tools. Only the server log showed the problem, as 500 error lines.

The cause sits in a dependency version inside the opencode binary. The 2.2.1
binary ships zod 4.6.7. The 2.2.0 binary ships zod 4.1.8. The AFT plugin
builds schemas for tools that zod 4.6.7 cannot convert. opencode catches the
conversion error for each tool and skips that tool.

## Detection

The server log carries one line for each skipped tool.

```bash
grep -c "Skipping invalid tool registration" ~/.local/share/opencode/log/opencode.log
```

The count was 500 on the Mac machine. A count above zero means that the tool
list lost members. The affected names appear in the same lines.

A second signal appears later. A tool call fails.

```text
Error: No tool named "bash" is currently available. Please use a tool from the available tool list.
```

## Timeline

All times are UTC and come from the log of the Mac machine.

| Time | Event |
|---|---|
| 2026-10-28T04:09:16Z | opencode 2.2.0 starts on the Mac machine |
| 2026-10-29T07:06:54Z | Update check reports that 2.2.1 is available |
| 2026-10-29T07:07:26Z | Bun installs `@opencode/cli@2.2.1`; the log states `updated OpenCode from=2.2.0 to=2.2.1` |
| 2026-10-29T07:07:41Z | The 2.2.1 server starts and loads the plugins, including AFT |
| 2026-10-29T07:07:43Z | The first 20 `Skipping invalid tool registration` errors appear |
| 2026-10-29T07:07:44Z | The same 20 tools fail again in the next registration round |
| 2026-10-29T07:11:11Z | The same 20 tools fail again |
| 2026-10-29T07:28:46Z | The last error line appears (log line 30569) |

The user sent the log to another machine on 2026-10-29. The analysis below
ran on Linux against `@opencode/cli` 2.2.0 and 2.2.1 with an isolated
`HOME`, so the tests never touched the live configuration.

## Root cause

Four facts form the chain.

**1. The 2.2.1 binary ships zod 4.6.7.** The root `package.json` catalog of
the opencode repository lists `"zod": "4.6.7"`. The same file in tag `v2.2.0`
lists `"zod": "4.1.8"`. The binary contains the zod copy, so the plugin does
not choose the version.

**2. zod 4.6.7 cannot convert a schema that has a custom JSON Schema
override and a parent.** In `zod/v4/core/to-json-schema.js`, the function
`processSchema` reads the custom method `schema._zod.toJSONSchema` at line
83. When that method exists, the code skips the branch at lines 104 to 108,
which registers the parent schema and sets `result.ref`. The function
`flattenRef` recurses into that parent at line 444. It has no lookup check,
and it reads `seen.ref` of an undefined entry at line 397. Bun reports
the result as `undefined is not an object (evaluating 'a.ref')`.

A standalone test shows the range. A zod 4.1.8 schema with a custom
override and a `.describe()` parent converts under zod 4.1.8 and 4.2.0. The
same schema throws under zod 4.3.0, 4.4.3, 4.5.4, 4.6.0, 4.6.5, 4.6.6, and
4.6.7.

**3. AFT builds exactly that schema.** In
`@cortexkit/aft-opencode@0.62.0`, the function `attachJsonSchemaOverride`
(`dist/entry/server.js:43923`) installs a custom `_zod.toJSONSchema` on every
argument schema. The function `renameArgumentDescriptions` (line 46011) calls
`.describe()` on the arguments. In zod v4, `.describe()` returns a clone that
keeps a link to the original schema as `_zod.parent`. The function
`projectV2Tool` (line 46104) joins the arguments with
`tool.schema.object(...)` and hands the result to the host.

**4. opencode converts the plugin schema with its own zod and skips the
tool on failure.** The function `standardJsonSchema` in
`packages/core/src/tool/runtime.ts:170` calls `toJSONSchema(schema, { target:
"draft-2020-12", io })` from the host copy of zod. The function `register` in
`packages/core/src/tool.ts:338` catches the TypeError and returns
`Invalid tool definition <id>: <message>`. The function `notify` in the same
file (line 230) writes the log line.

The version table in the cache entry holds the test matrix. The short form:
AFT alone reproduces the failure on 2.2.1. The other five plugins never
reproduce it. opencode 2.2.0 with the same AFT is clean. AFT keeps every
tool on 2.2.1 when the custom override is off.

## Impact

- The Mac machine lost all file and shell tools. The agent could not read,
  write, or edit a file, and could not run a command.
- The failure was silent in the user interface. The session looked healthy.
- The log grew by 500 error lines in 21 minutes. Each registration round
  repeats the same 20 errors.
- The host that runs this dotfiles sits on opencode 2.2.0. The dotfiles pin
  the plugin as `@cortexkit/aft-opencode@latest`, so the next CLI update on
  any machine repeats the failure.
- The 2.2.1 release notes list no change to plugin tool registration. The
  zod bump does not appear as a breaking change.

## Resolution

Downgrade the CLI on the affected machine.

```bash
bun install --global --trust @opencode/cli@2.2.0
```

The second option is to remove `@cortexkit/aft-opencode@latest` from the
`plugins` list in `~/.config/opencode/opencode.jsonc`. This restores the
builtin file and shell tools. It also removes the AFT tools, so the
downgrade is the better option.

## Action items

1. **File a zod issue.** The fix is a lookup check in `flattenRef` before the
   recursion into `schema._zod.parent`. The reproduction uses a schema with
   a custom `_zod.toJSONSchema` and a `.describe()` parent.
2. **File an AFT issue.** The plugin can keep the override only if the host
   copy of zod matches the plugin copy. A safer design removes the override
   and lets the host strip the `$schema` key.
3. **File an opencode issue.** The binary converts a plugin schema with its
   own zod copy. A version mismatch inside the binary breaks plugins that
   the binary does not own. The release notes should list the zod bump as a
   breaking change for plugins.
4. **Pin the CLI version** on every machine until one of the three fixes
   lands. Check the version after each update.
5. **Re-check the cache entry** at each AFT or zod release. The entry is
   `.agents/docs/cache/opencode-harness/2026-10-29-opencode-2-2-1-zod-tool-registration.md`.

## Lessons learned

- **A dependency bump inside a binary breaks plugins that the binary does
  not own.** The plugin did not change. The host changed the rules that the
  plugin must satisfy.
- **A per-tool skip is not a fatal error.** opencode logged 20 errors and
  continued. The session started with a smaller tool list, and no message told
  the user.
- **The error text names the step, not the library.** The message names the
  property `a.ref`. It does not name zod, and it does not name AFT.
- **The update came from the tool itself.** The CLI installed a new version
  in the background. Any change to that behavior needs the same review as a
  manual update.
- **Two libraries that must agree need one owner.** The host and the plugin
  both ship zod. The plugin cannot pin the host copy, and the host cannot
  know the plugin copy.

## See also

- `.agents/docs/cache/opencode-harness/2026-10-29-opencode-2-2-1-zod-tool-registration.md`
  — the reusable fact and the test matrix
- `docs/post-mortem/2026-10-28-overlong-variant-research-loop.md` — the
  earlier post-mortem from the same project
