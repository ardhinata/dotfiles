# Processes That Outlive One Command

Three kinds of work outlive a single command. Use the harness's own
long-running tools, not shell backgrounding. Tool names differ per harness —
the concepts do not.

## Background processes — dev servers, watchers, daemons

For anything that must keep running (`npm run dev`, `vite`, `next dev`,
`bun --watch`, test watchers, local services), start it through the harness's
background-process facility. Never use `&`, `nohup`, `disown`, or `setsid`.
A tracked background process stays visible to the harness and can be read or
killed later. A detached shell process is invisible and leaks.

When the harness has no background facility, say so and run the command in the
foreground.

## Fan-out — parallel sessions, worktrees, subagents

Use the fan-out facility when the user asks for parallel work, worktrees, or
multiple independent sessions. For ordinary delegated research, use the plain
subagent tool.

## Waiting for a command to finish

`sleep` never waits for anything. It is a command that ends after N seconds.
It does not observe the build, the job, or the agent you care about.

- Never poll a task inspector in a loop. Watch the task instead.
- Do not chain work onto a sleep. `sleep 60 && next-step` never reaches
  `next-step` unless a watcher picks it up.
- For agent fan-out, wait for the agent's report. Do not sleep and poll.
