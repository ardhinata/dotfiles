# Processes That Outlive One Command

Two kinds of work outlive a single command. Use the dedicated tools, not shell
backgrounding. Tool names differ per harness — the concepts do not.

## Background processes — dev servers, watchers, daemons

For anything that must keep running (`npm run dev`, `vite`, `next dev`,
`bun --watch`, test watchers, local services), start it through the harness's
background-process facility. Never use `&`, `nohup`, `disown`, or `setsid`.
A tracked background process stays visible to the harness and can be read or
killed later. A detached shell process is invisible and leaks.

| Harness | Facility |
|---|---|
| OpenCode | the shell tool's background mode |

## Fan-out — parallel sessions, worktrees, subagents

Use the fan-out facility when the user asks for parallel work, worktrees, or
multiple independent sessions. For ordinary delegated research, use the plain
subagent tool.

| Harness | Worktree facility | Delegated research |
|---|---|---|
| OpenCode | `opencode.worktree_create` | `subagent` tool |
