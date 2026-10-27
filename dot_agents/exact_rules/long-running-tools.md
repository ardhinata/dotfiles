# Processes That Outlive One Command

Three kinds of work outlive a single command. Use the dedicated tools, not
shell backgrounding. Tool names differ per harness — the concepts do not.

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

## Waiting for a command to finish

`sleep` never waits for anything. It is a command that ends after N seconds.
It does not observe the build, the job, or the agent you care about.

The harness auto-promotes a long foreground command to the background. The
promotion notice means the command is still running. It is not a result, and
it carries no exit code. Only a task result proves that work finished.

| Need | Concept | OpenCode facility |
|---|---|---|
| Block until a command ends | wait on the task | `shell({ command, wait: true })` |
| Block on a task already running | watch the task | `bash_watch({ taskId })` |
| Look at a task once | inspect the task | `bash_status({ taskId })` |
| Stop a running task | kill the task | `bash_kill({ taskId })` |

- Never poll the inspector in a loop. Watch the task instead.
- `wait: true` detaches to the background when a new message arrives. The
  command keeps running. A later message is not proof that it finished.
- Do not chain work onto a sleep. `sleep 60 && next-step` never reaches
  `next-step` unless a watcher picks it up.
- For agent fan-out, wait for the agent's report. Do not sleep and poll.
