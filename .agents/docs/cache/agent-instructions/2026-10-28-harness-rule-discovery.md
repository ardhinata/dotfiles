---
source:
  - https://opencode.ai/docs
  - https://docs.anthropic.com/en/docs/claude-code
captured: 2026-10-28
freshness: check-2027-01
tags: [agent-rules, harnesses, opencode]
---

# How each harness discovers agent rule files

No harness discovers `~/.agents/rules/` natively; each loads rule files through
its own instruction mechanism, and on this host only OpenCode has one.

Captured 2026-10-28 while deciding which rule files are OpenCode-specific and
which are shared. A research subagent checked the official documentation of
every harness the house rules target.

## Finding

`~/.agents/rules/` and `~/.agents/rules.personal.d/` are a house convention,
not a platform feature. Each harness loads them through its own instruction
mechanism, and on this host only OpenCode has one.

## Evidence

| Harness | Mechanism | Can it load a directory of files |
|---|---|---|
| OpenCode | `instructions` globs in `opencode.jsonc` | yes |
| Copilot CLI | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | yes, with filename constraints |
| Claude Code | `CLAUDE.md` and named files | no |
| Codex | `AGENTS.md` and named files | no |
| Cursor | `AGENTS.md` and named files | no |
| Gemini CLI | `GEMINI.md` | no |
| Zed | `AGENTS.md` and named files | no |
| goose | `.goosehints` | no |
| Amp | `AGENTS.md` | no |
| Factory Droid | `AGENTS.md`; `~/.agents/` treated as a personal instruction directory, recursion undocumented | unknown |

**Residual risk.** No documented glob picks up `~/.agents/rules.opencode/`.
Factory Droid's scan of `~/.agents/` is undocumented and may recurse; the
existing `rules.personal.d/` carries the same exposure.

**The per-harness facility equivalents.** A shared rule that names one
harness's tool has no counterpart in the others:

| Need | OpenCode | Claude Code | Codex | Cursor | Gemini CLI | goose / Amp |
|---|---|---|---|---|---|---|
| background process | shell tool background mode | Bash `run_in_background` | shell background | terminal background | shell background | none known |
| watch / inspect / kill a task | `bash_watch`, `bash_status`, `bash_kill` | `Monitor`, `TaskStop`, `/tasks` | `write_stdin` polling | none known | none known | none |
| fan-out to worktrees | `opencode.worktree_create` | worktrees | none known | none known | none known | none |
| delegated research | `subagent` tool | subagents | subagents | agents | subagents | subagents |
| dedicated code search | AFT `aft_search`, `aft_outline`, `aft_zoom`, `glob`, `grep`, `read` | read-only tools | read-only tools | codebase indexing | read-only tools | read-only tools |
| web search and fetch | `websearch`, `webfetch` | `WebSearch`, `WebFetch` | `google_web_search`, `web_fetch` | `search_web`, `fetch` | `google_web_search`, `web_fetch` | varies |
| ask the user a closed question | `question` tool | `AskUserQuestion` | none | "Ask questions" | `ask_user` | none / `AskUser` in Factory |
| shell with a pty | shell tool pty mode | none known | none known | none known | none known | none |
| choose the shell binary | `shell` key in `opencode.jsonc` | none known | none known | terminal profile | none known | none |

## Why it matters

The shared rule tree is, in practice, OpenCode's own load path. Moving a rule
out of it changes little for the other harnesses, because they were never
reading it. The OpenCode-scoped split is therefore a clarity and cost
decision, not a compatibility fix.

Where a harness has no equivalent, a shared rule must stay generic and name
the concept, not the tool.

## Scope

Ten harnesses, checked against official documentation on 2026-10-28. Factory
Droid's behaviour is partly undocumented.

## Uncertainty

Re-verify after any harness release that changes its instruction mechanism.
The Factory Droid entry is the weakest: its scan of `~/.agents/` may recurse.

## Sources

- Official documentation for OpenCode, Claude Code, Codex, Copilot CLI,
  Cursor, Gemini CLI, Zed, goose, Amp, Factory Droid.

## See also

- `docs/plans/2026-10-28-agent-instruction-scope-and-ste-checker.md` — the
  plan this entry came from
- `.agents/docs/cache/agent-instructions/2026-10-26-always-on-instruction-files.md`
  — the cost side of the same trade
