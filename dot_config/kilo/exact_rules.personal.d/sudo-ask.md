Privilege escalation must always be confirmed with the user — even when the tooling supports silent elevation.

## When

Any command that would elevate to root, either directly or transitively:

- Direct invocations: `sudo ...`, `sudo -E ...`, `pkexec ...`, `doas ...`.
- Any shell pattern that ends up elevating (e.g. `sudo bash -c "..."`, passwordless escalation helpers, distro wrappers that internally call `sudo`).
- A tool whose output implies root was silently elevated (e.g. an install step "ran successfully" with no prompt) — stop and re-ask.

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
