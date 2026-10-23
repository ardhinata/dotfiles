# Long-Running Tools

Two kinds of work outlive a single command. Use the dedicated tools, not shell
backgrounding. Tool names differ per harness — the concepts do not.

## Background processes — dev servers, watchers, daemons

For anything that must keep running (`npm run dev`, `vite`, `next dev`,
`bun --watch`, test watchers, local services), start it through the harness's
background-process facility — **not** `&`, `nohup`, `disown`, `setsid`, or
`Start-Process`. A tracked background process stays visible to the harness and
can be read from or killed later; a detached shell process is invisible and
leaks.

| Harness | Facility |
|---|---|
| Kilo | `background_process` `start` |
| OpenCode | the shell tool's background mode |

## Fan-out — parallel sessions, worktrees, subagents

Use the harness's fan-out facility only when the user explicitly asks to fan
out work, create worktrees, or start multiple sessions for independent tasks.
Do **not** use it for ordinary delegated research — that is the plain subagent
tool.

| Harness | Facility |
|---|---|
| Kilo | `agent_manager` (worktrees) and `task` (subagents) |
| OpenCode | `opencode.worktree_create` and the `subagent` tool |
