---
date: 2026-11-07
scope: OpenCode v2.2.6, @cortexkit/aft-opencode 0.62.x, @cortexkit/opencode-magic-context 0.49.25, opencode-orchestrator 2.0.21
status: verified live on this host where marked
---

# Subagent memory and orchestrator handback

This report answers one design question: can a coding-agent orchestrator supervise subagents
with full memory recall and store, on this stack? All live results below come from this
host on 2026-11-07.

## Tool access by subagent type

| Tool | `general` subagent | `explore` subagent |
|---|---|---|
| `aft_search`, `aft_inspect`, `aft_callgraph` | works | not visible |
| `ctx_search`, `ctx_expand`, `ctx_reduce` | works | not visible |
| `ctx_memory`, `ctx_note` | never exposed | never exposed |
| Memory MCP server tools | works with allow rules | not visible |

Findings, with evidence:

- `ctx_memory` and `ctx_note` stay out of subagent sessions by design. The gate is
  `PRIMARY_ONLY_TOOLS = new Set(["ctx_memory", "ctx_note"])` in the Magic Context bundle
  (`dist/index-y6xpzjzr.js:26904`). Magic Context internal children (dreamer, historian)
  bypass the gate. No user config exists to change this.
- `explore` agents drop all plugin tools. Their permission block denies all and allows a
  short list (`shell`, `grep`, `glob`, `webfetch`, `websearch`, `read`). A per-agent allow
  rule for the `aft_*` tools would carry AFT into an explore variant. Not applied.
- MCP tools work inside a subagent after one change: the agent frontmatter needs an explicit
  permission allow per MCP server or tool. Verified end to end in an isolated HOME with
  `@modelcontextprotocol/server-memory` (`/tmp/opencode/mc-subtest/`). The agent wrote an
  entity and read it back with no error. Background context: the upstream issue is
  `opencode` #16491. Without the allow rules, execution fails.
- AFT detects subagent sessions by `parentID` (`src/shared/subagent-detect.ts`). It adapts
  by refusing `background: true` shell calls and by disabling auto-promotion, because a
  waiting subagent would end its turn.

## Memory store tiers

- **Tier 0 (chosen)** — orchestrator handback. The worker writes a handoff file and returns
  findings plus position. The orchestrator stamps one `ctx_note` with task, path, position,
  and the session pointer. Durable decisions go to `ctx_memory`. Repo conventions stay in
  repo files. One writer keeps the Magic Context consolidation logic correct and avoids the
  shared-memory-poisoning failure mode.
- **Tier 1 (verified, optional)** — a subagent stores to its own local MCP memory server.
  Works today with the permission allow rules. Cost: a second store beside Magic Context.
- **Tier 2 (not available)** — `ctx_memory` directly in subagents. Requires a CortexKit
  feature change.

## Handback and resume behavior

Live results:

- A completed subagent re-opened with the same `sessionID` reproduced its exact facts
  without new tool calls. Verified at a 25 minute age and across a `/ctx-dream` run.
- A worker child from about 2 hours earlier failed with `Subagent session not found`. The
  cause stays unproven: deletion, or a stale recorded id. The list table for the cause was
  not reachable, because cc-safety-net blocks reads of `~/.local/share/opencode/opencode.db`.
- Subagent sessions appear with zero rows in `compartment_chunk_embeddings`. The Magic
  Context historian does not chunk child transcripts into the searchable project history.
  `ctx_search` therefore cannot bring back child-only knowledge. All worker knowledge must
  pass through the handoff file or a note before the child session ends.
- `keep_subagents: false` (the default in `dot_config/cortexkit/magic-context.jsonc`)
  deletes Magic Context internal child sessions at settle.
  `src/shared/child-session-teardown.ts` implements this. `keep_subagents: true` keeps every
  settled child at a retention cost.

The operation rule for the orchestrator: the handoff file is the source of truth. The
`sessionID` is a shortcut for one work window. When a pointer is dead, respawn a fresh
child and seed it from the handoff file. This pattern is lossless. See session note #15 and
project memories #190 and #191.

## opencode-orchestrator decision

The plugin returns value at project scale, so it came back:

- Restored in `dot_config/opencode/private_opencode.jsonc` and amend-committed as
  `5cdb0f0`. The deployed target `~/.config/opencode/opencode.jsonc` already carried the
  entry. So we did not run `chezmoi apply`.
- `update_todo` comes from this plugin. A plugin-free headless run has no such tool.
- It adds mission state in `.opencode/`, the Commander, Planner, Worker and Reviewer role
  presets, secret redaction in tool output, and a message size guard.
- The Magic Context conflict detector has no entry for it. The two run together.

## CMS build recipe

- **Without spec-kit.** The Commander starts one mission per phase (schema, content store,
  media, page rendering, admin, search, tests). Each Worker ends with a handoff file and a
  note. The Commander merges files into mission state and moves to the next phase.
- **With spec-kit.** `specify init <project> --integration opencode`. The `opencode`
  integration is official. Command syntax is the dash form: `/speckit-specify`,
  `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`. The bridge
  is one orchestrator mission per unchecked task in `tasks.md`. `/speckit-converge` serves
  as the review role. Division of labor: spec-kit owns what to build, the orchestrator owns
  who runs and when, Magic Context owns decisions and history.

## Rejected alternatives

- `oh-my-openagent` — the Magic Context conflict detector finds its hook family and Magic
  Context disables itself. Disqualified.
- MemPalace and Graphify — each adds a parallel memory or index layer beside one that
  already exists. AFT and Magic Context already cover their roles.
- Hosted memory services (Mem0, Supermemory, Mnemoverse) — conflict with the rule that
  forbids paid endpoints.
- The `CodingAgentOrchestration` guide stays useful for three rituals only: a periodic PR
  review prompt for better rules, a confidence score in the loop, and a periodic
  self-audit of the whole setup.

## Limits and open items

- The server log gave no clear internal-child teardown line around the dream run. The
  count of lines that match the keywords moved from 905 to 911 only. So the
  `keep_subagents: false` delete mechanic rests on the source and its design comments,
  not on a log sample.
- The exact expiry time of a `sessionID` pointer is unknown. Treat ages over about one
  hour as already expired.
- Scratch state from the MCP experiment lives at `/tmp/opencode/mc-subtest/` and is safe
  to remove.

## References

- Magic Context plugin source (local):
  `~/.cache/opencode/npm/@cortexkit/opencode-magic-context@0.49.25/1793151287453/node_modules/@cortexkit/opencode-magic-context/src/`
  (`agents/permissions.ts`, `shared/subagent-detect.ts` in the AFT tree,
  `shared/child-session-teardown.ts`, `shared/keep-subagents.ts`)
- Handback ledger: session note #15, project memories #190 and #191
- Experiment config and data: `/tmp/opencode/mc-subtest/`
- Handoff sample: `/tmp/opencode/handoffs/cms-workers.md`
- Rule file citations from research: `~/.agents/rules.personal.d/scoped-searches.md`
