# Streaming Over SSH

Over `ssh` without a pty, the remote stdout is a pipe, so libc-style programs
block-buffer and print only at exit.

For live remote output:

- Dynamically linked commands: wrap them in `stdbuf -oL`.
- Python: use `python -u` or `PYTHONUNBUFFERED=1`. `stdbuf` does not affect
  it.
- Static binaries, a missing `stdbuf`, or any other case: use `ssh -tt`. It
  merges stderr into stdout and turns `\n` into `\r\n`.

Do not use `nohup`, `&`, or `disown` to fix buffering. Use the harness
background facility.
