# Bash Tool — zsh Emulation Fallback

The shell tool runs each command as `<shell> -c "<command>"`: a fresh,
non-interactive, non-login shell. **No rc file is loaded** — no `~/.zshrc`,
no `~/.bashrc`, no aliases, no `setopt`/`shopt` from the user's interactive
session. zsh and bash default to different behavior for some shell constructs
even when the script "looks the same."

## Which shell is the tool using?

The harness picks the binary. OpenCode reads the `shell` config field
(`~/.config/opencode/opencode.jsonc`); when it is absent it falls back to
`$SHELL`. This host pins `"shell": "/usr/bin/bash"`, so tool commands run in
bash. Verify with one call when it matters:

```sh
echo "$0"; echo "${BASH_VERSION:-no-bash}${ZSH_VERSION:-no-zsh}"
```

`$0` is the literal binary path (`/usr/bin/bash`), and `BASH_VERSION` /
`ZSH_VERSION` tells you which shell semantics apply.

## When

A shell-tool invocation fails with a zsh-specific error that bash would not
produce, **and** the command looks bash-portable. Common symptoms:

- `zsh: command not found: ...` for a construct that bash parses as a builtin (e.g. `[[ ... ]]` when you meant `[ ... ]`).
- `zsh: parse error near ...` near `((` arithmetic, here-string `<<<`, or process substitution `<(...)`.
- A pattern using bash-only glob semantics that zsh's extended glob misinterprets.

## The fallback — what actually works

**`emulate -LR sh` does not do what its name suggests in zsh.** The `-L` flag
in zsh means "local to the immediately surrounding shell function, if any"
(see `man zshmisc` §"Shell Builtin Commands" → `emulate`). At the top level
of an interactive session or of `bash -c '...'`, there is no surrounding
function, so `-L` is silently ignored and the sh emulation **leaks into the
persistent session** — every subsequent invocation inherits NO_NOMATCH,
KSH_ARRAYS, and POSIX_BUILTINS-adjacent behaviour until the session ends.

That is almost never what you want. Instead:

1. **For a single command**, run it under `bash -c '...'` so the shell
   semantics are scoped to the subshell and nothing leaks:

   ```bash
   bash -c 'mv /etc/nginx/conf.d/*.conf /tmp/old-$(date +%F)/'
   ```

2. **For real bash semantics** (not just sh-shaped options), use `bash -c '...'`
   with `shellcheck -s sh` validation. `emulate sh` does not change zsh syntax
   (`[[ ]]`, `(( ))`, `<(...)`, parameter flags, zsh-only variables like
   `$ZSH_VERSION`); it only flips option flags. If you wrote zsh syntax and
   ran `emulate -LR sh` in front of it, the command breaks differently than
   the original failure.

3. **For a script** that must be portable, write it to a temp file with
   `#!/bin/sh` and run it. Do not lean on shell-emulation tricks to make a
   zsh-shaped script "act bash".

## The user's interactive shell is a separate thing

`dot_shell/zsh/00-before-zgenom.zsh:29` runs `unsetopt NOMATCH` for the
**interactive prompt** — the zsh the user types into. That does not reach the
tool, because the tool loads no rc file. Do not reason about tool behavior
from the state of the interactive session.

## Anti-patterns

- Prefix any command with `emulate -LR sh` "to be safe" — leaks sh emulation into the rest of the session and breaks zsh features you actually want.
- Reach for `emulate sh` when the real fix is a different **shell** — zsh's `**`, `(a|b)` extended glob, and `$array[(i)val]` look zsh-natural but break in bash too. If the script must be portable, use `find` / `case` / explicit loops, not simulation tricks.
- Add `emulate sh` to your interactive `.zshrc` — kills zsh features you'll want at the prompt. Per-command only.
- Assume the tool inherits your interactive shell's options or aliases — it does not. `alias` count is 0 inside a tool call.
- Try `unsetopt NOMATCH` "again" to fix a `no matches found` error in a tool call — that option is not set in the tool's shell, so the error means the shell is zsh, not that the option was lost.
