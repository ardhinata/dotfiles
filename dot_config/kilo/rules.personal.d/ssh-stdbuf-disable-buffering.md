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

Prefer `-oL -eL` together so both stdout and stderr are line-buffered.

## Caveats

- `stdbuf` works via `LD_PRELOAD`; it has **no effect on statically-linked binaries** (busybox `ash`, some Go binaries built with `CGO_ENABLED=0`, rust static musl builds). If `ldd $(command -v <bin>)` reports "not a dynamic executable" or `file` says "statically linked", use `ssh -tt` instead.
- `ssh -tt` forces a tty, which can break non-tty-friendly commands (color codes, progress bars that detect a tty and switch to alternate screen buffers). If output is now too noisy, drop `-tt` and accept buffered output, or pipe through `less -R`.
- `stdbuf` only affects the wrapped process and its dynamically-linked children. A statically-linked grandchild still buffers.

## Anti-patterns

- Reaching for `nohup` / `&` / `disown` to "fix" ssh output buffering — buffering comes from the pipe, not from job control.
