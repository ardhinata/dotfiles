# Ensemble team operation

Rules for the lead when the opencode-ensemble plugin runs a team.

## When

These rules apply when the opencode-ensemble plugin is active and you are the
lead of a team. The plugin injects the role and the tool list itself. It also
injects the commit and merge steps. These rules cover what it does not inject.

## Teammate reports go to a file

- The plugin limits `team_message` content to 10 KiB. The limit is a hard error
  at send time. A teammate with a long report prunes it and wastes its budget.
- Every `team_spawn` prompt tells the teammate to write the full findings to
  `docs/agent-reports/<teammate>.md` in its worktree.
- The prompt also tells the teammate to commit that file. The teammate sends
  one `task-result` message. Its `summary` holds one line. Its `details` holds
  the pointer.
- Use the report directory that the project names, when it names one.
- The lead reads the file, not the message. Before the merge, read the
  absolute worktree path. After the merge, the repo-relative path works,
  because the committed file arrives with the branch.
- A teammate that runs as `explore` cannot write files. It reports in the
  message and keeps the report short. Or you spawn it as `general`.

## Waiting for teammates

- Never use `sleep` to wait for a teammate. A sleep does not wait.
- Teammates report when they finish. End your turn and let the message arrive.
- The plugin sends a stall notice after `stallThresholdMs` of silence. The
  default is 5 minutes. The notice means the teammate is quiet. It does not
  mean the teammate failed. Message the teammate first. Stop the teammate only
  after it reports that it is stuck.
- `team_shutdown` without `force` lets the teammate finish and keeps its
  branch. Use `force` only when the teammate ignores a shutdown request.

## Anti-patterns

- Do not stop a teammate because a stall notice arrived.
- Do not paste a full report into the body of a `team_message`.
- Do not wait on a teammate with `sleep` or with a poll loop.

## References

- `~/.agents/skills/opencode-ensemble/SKILL.md` — team shapes and prompts.
- `~/.config/opencode/ensemble.json` — `stallThresholdMs`, `timeoutMs`,
  `modelPool`.
