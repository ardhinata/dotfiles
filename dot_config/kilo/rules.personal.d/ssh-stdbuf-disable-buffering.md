When running commands over `ssh`, the remote process's stdout/stderr is attached to a non-tty pipe and becomes **block-buffered** — streaming output (build progress, `tail -f`, log tailing, `npm/pip/cargo` progress bars) appears in bursts or only at exit. Apply `stdbuf -oL` to fix this.

## When

About to run a long-running or streaming command over `ssh` where live, line-by-line output matters:

- `ssh host 'npm run build'`, `ssh host 'cargo test'`, `ssh host 'make'`
- `ssh host 'journalctl -fu ...'`, `ssh host 'tail -f /var/log/...'`
- `ssh host 'python -u script.py'` — also valid, prefer `stdbuf -oL` for general commands
- Any `ssh ... '...'` where the remote side is not allocating a tty and output feels laggy

## Pick the right place to apply `stdbuf`

| Case | Apply to | Example |
|---|---|---|
| Remote command is **dynamically linked** (most distros' userland) | The remote command itself | `ssh host 'stdbuf -oL -eL ./build.sh'` |
| Remote binary is **statically linked** or `stdbuf` is unavailable on the remote | Wrap the **remote command in a pty** via `ssh -tt` | `ssh -tt host './build.sh'` |
| Local `ssh` itself prints streaming output (e.g. progress meters, `tail -f` of a remote file via local proxy) | Wrap local `ssh` | `stdbuf -oL -eL ssh host 'tail -f file'` |

Prefer `-oL -eL` together so both stdout and stderr are line-buffered (stderr is unbuffered by default but wrapper scripts can change that).

## Recipe

```bash
# Remote command — most common case
ssh host 'stdbuf -oL -eL <command>'

# When remote stdbuf is missing or binary is static — force a pty
ssh -tt host '<command>'

# Local ssh proxy — for tools like `ssh host tail -f | <local viewer>`
stdbuf -oL -eL ssh host 'tail -f /var/log/x.log'

# Combine when in doubt (line-buffer locally + allocate pty remotely)
stdbuf -oL -eL ssh -tt host 'stdbuf -oL -eL <command>'
```

## Caveats

- `stdbuf` works via `LD_PRELOAD`; it has **no effect on statically-linked binaries** (busybox `ash`, some Go binaries built with `CGO_ENABLED=0`, rust static musl builds, busybox applets). Check with `ldd $(command -v <bin>) | grep -q 'not a dynamic executable'` or just `file $(command -v <bin>)` — if `statically linked`, use `ssh -tt` instead.
- `ssh -tt` forces a tty, which can break non-tty-friendly commands (color codes, progress bars that detect a tty and switch to alternate screen buffers). If output is now too noisy, drop `-tt` and accept buffered output, or pipe through `less -R`.
- `stdbuf` only affects the wrapped process and its dynamically-linked children. A statically-linked grandchild still buffers.

## Anti-patterns

- Reaching for `nohup` / `&` / `disown` to "fix" ssh output buffering — buffering comes from the pipe, not from job control.
- Running the same command with `2>&1 | cat` on the remote and expecting line-buffering — `cat` is a no-op for buffering; you need `stdbuf` or a tty.
- Re-typing the same `stdbuf -oL` wrapper every session instead of an alias or `SendEnv` — see below.

## Make it sticky (optional)

```sh
# In dot_zshrc (or equivalent): wrap the common cases
alias ssh-build='ssh -tt'
# Or a helper that auto-wraps streaming-looking commands:
ssh-stream() { ssh -tt "$@"; }
```

For per-host defaults, edit `~/.ssh/config`:

```
Host *
  RequestTTY no        # default: don't allocate tty
Host stream-*
  RequestTTY force      # these aliases always allocate a pty
```

Then `ssh stream-prod 'make'` automatically gets a pty without remembering `-tt`.

## References

- `man stdbuf` — `-oL` line-buffer stdout, `-eL` line-buffer stderr, `-iL` line-buffer stdin
- `man ssh` — `-tt` "Force pseudo-terminal allocation"; `RequestTTY` in ssh_config
- `dot_ssh/config` — current per-host `RequestTTY` and `Match` patterns in this repo
- `~/.config/kilo/rules.personal.d/ssh-agent-keys-location.md` — gpg-agent SSH key wiring (orthogonal but often used together)