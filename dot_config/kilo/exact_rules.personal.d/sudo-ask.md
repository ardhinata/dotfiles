Privilege escalation must always be confirmed with the user — even when the tooling supports silent elevation.

## When

Any command that would elevate to root, either directly or transitively:

- Direct invocations: `sudo ...`, `sudo -E ...`, `pkexec ...`, `doas ...`.
- Any shell pattern that ends up elevating (e.g. `sudo bash -c "..."`, passwordless escalation helpers, distro wrappers that internally call `sudo`).
- A tool whose output implies root was silently elevated (e.g. an install step "ran successfully" with no prompt) — stop and re-ask.

## Detect before asking

The escalation shape changes the question you ask. Spend one tool call to learn it before forming the `question`:

1. **Headless?** Run `tty -s && echo tty || echo notty`. If `notty`, you have no tty to attach a pinentry to; interactive `sudo` will hang. Note this in the question.
2. **Passwordless for this command?** Run `sudo -n -l <command> 2>&1`. A line like `NOPASSWD: /usr/bin/apt` means the command is silently allowed for the current user; ask whether to use that lane or pause for explicit approval anyway.
3. **Effective environment for env-preserving flags?** If the user might want `sudo -E`, list the env vars the command actually reads (`systemctl show-environment`, `env | grep …`) so the question can name them.

Use these signals in the `question` body, not as a substitute for asking.

## Process

1. Surface the **exact command(s)** and a one-line reason via the `question` tool.
2. Wait for explicit approval before running anything that requires root.
3. **Re-confirm per command** — previous approval does not carry forward to a new command.
4. If the user denies, do not retry, do not look for an alternative escalation path, do not use `pkexec`/`doas` as a workaround unless the user names them.

## Anti-patterns

- Running `sudo` because "the next step needs it anyway" — ask first.
- Treating `NOPASSWD` in `/etc/sudoers` as blanket permission — the rule is per-command, not per-session.
- Using `sudo -E` to preserve env without disclosing the env it preserves.
- Assuming interactive `sudo` always fails in this environment — it can work via `interactive_terminal`; the rule still applies.
- Assuming `sudo` will fail just because there is no tty — the user may have configured `NOPASSWD` for that command. Detect with `sudo -n -l`; do not assume.
- Running `sudo` in a headless context without warning the user — interactive `sudo` hangs on a missing pinentry; the question must mention this when `tty -s` fails.
