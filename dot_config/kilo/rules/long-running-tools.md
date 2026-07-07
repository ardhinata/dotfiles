# Long-Running Tools (`background_process`, `agent_manager`)

Two tools manage work that outlives a single command. Use the dedicated tools, not shell backgrounding.

## `background_process` — dev servers, watchers, daemons

For anything that must keep running (`npm run dev`, `vite`, `next dev`, `bun --watch`, test watchers, local services), use `background_process` `start` — **not** `&`, `nohup`, `disown`, `setsid`, or `Start-Process`. Started processes are tracked and visible in the CLI sidebar.

- Pass `ready.pattern` when the process prints a recognizable line (`ready`, `Local:`, `started server`).
- Pass `ready.port` when it should accept TCP on a known port.
- Omit `ready` only when readiness is unknowable — the process is reported running immediately.
- `persistent: true` survives session/Kilo restart; `inherit: true` (subagents only) transfers to the parent session. Never combine them.
- Manage with `list` / `status` / `logs` / `restart` / `stop`. Each requires the `id` returned by `start`; never invent an `id`.

## `agent_manager` — fan-out to parallel Agent Manager sessions

Use `agent_manager` only when the user explicitly asks to fan out work, create Agent Manager worktrees, or start multiple sessions for independent tasks. Do **not** use it for ordinary subagent research — that is the `task` tool.

- `mode: worktree` → isolated git worktrees (like the New Worktree dialog); `mode: local` → same-directory sessions.
- Pick `model` by name (e.g. "Claude Opus 4.1"); matching is lenient. Resolve candidates first via `agent_manager_models` if unsure.
- Set `versions: true` **only** when tasks are alternate versions of the same work to compare. Default is independent sessions.
- Keep `name` short — Agent Manager cards are narrow. Branch names are sanitized from `branchName`.
