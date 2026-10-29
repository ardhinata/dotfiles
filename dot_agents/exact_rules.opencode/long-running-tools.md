# Processes That Outlive One Command — OpenCode

OpenCode facility names for the shared rule
`~/.agents/rules/long-running-tools.md`.

| Need | OpenCode facility |
|---|---|
| Run a command that keeps running | the shell tool's background mode — `shell({ background: true })` |
| Block until a command ends | `shell({ command, wait: true })` |
| Watch a running task | `bash_watch({ taskId })` |
| Inspect a task once | `bash_status({ taskId })` |
| Stop a running task | `bash_kill({ taskId })` |
| Create an isolated worktree | `opencode.worktree_create` |
| Delegate research | the `subagent` tool |

- A long foreground command is auto-promoted to the background. The promotion
  notice means the command is still running. It is not a result, and it
  carries no exit code. Only a task result proves that work finished.
- `wait: true` detaches to the background when a new message arrives. The
  command keeps running. A later message is not proof that it finished.
- `bash_watch` in async mode needs a `pattern` and returns immediately. Sync
  mode waits. `bash_status` is a one-shot inspector — never a polling loop.
- `shell({ pty: true })` gives the command a terminal.
