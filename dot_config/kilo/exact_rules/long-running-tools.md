# Long-Running Tools (`background_process`, `agent_manager`)

Two tools manage work that outlives a single command. Use the dedicated tools, not shell backgrounding.

## `background_process` — dev servers, watchers, daemons

For anything that must keep running (`npm run dev`, `vite`, `next dev`, `bun --watch`, test watchers, local services), use `background_process` `start` — **not** `&`, `nohup`, `disown`, `setsid`, or `Start-Process`. Started processes are tracked and visible in the CLI sidebar.

## `agent_manager` — fan-out to parallel Agent Manager sessions

Use `agent_manager` only when the user explicitly asks to fan out work, create Agent Manager worktrees, or start multiple sessions for independent tasks. Do **not** use it for ordinary subagent research — that is the `task` tool.
