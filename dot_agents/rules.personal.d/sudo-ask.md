# Sudo Needs Approval

Privilege escalation must be confirmed with the user, even when the tooling
allows silent elevation.

## When

Any command that would elevate to root, directly or transitively:

- `sudo ...`, `sudo -E ...`, `pkexec ...`, `doas ...`
- A wrapper that ends up elevating, such as `sudo bash -c "..."` or a distro
  helper that calls sudo internally
- A tool whose output implies root was silently elevated — stop and re-ask

## Detect before asking

One tool call tells you the shape of the escalation. Put the result in the
question.

1. **Terminal?** `tty -s && echo tty || echo notty`. A non-interactive tool
   shell has no tty. Interactive sudo then fails fast with "a terminal is
   required to read the password". It does not hang here.
2. **Passwordless?** `sudo -n true 2>&1`. Exit 0 with no output means sudo
   runs without a password, so the target command runs too. "sudo: a password
   is required" means the escalation needs the user's password. `sudo -n -l`
   does not answer this: listing the sudoers rules also needs a password.
3. **Environment for `sudo -E`?** List the env vars the command reads
   (`systemctl show-environment`, `env | grep …`) so the question can name
   them.

## Process

1. Surface the exact command and a one-line reason with the harness's
   question tool, or in plain text.
2. Wait for explicit approval before running anything that needs root.
3. Re-confirm per command. Earlier approval does not carry forward.
4. If the user denies, do not retry, and do not look for another escalation
   path. Do not use `pkexec` or `doas` as a workaround unless the user names
   them.

To give sudo a terminal, run it through the shell tool's pty mode, when the
harness has one.
