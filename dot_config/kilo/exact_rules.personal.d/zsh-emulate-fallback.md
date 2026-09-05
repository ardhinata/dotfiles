# Bash Tool — zsh Emulation Fallback

The `bash` tool runs each command inside this zsh session. zsh and bash default to different behavior for some shell constructs even when the script "looks the same."

## Global state already handles the common cases

`dot_shell/zsh/00-before-zgenom.zsh:29` runs `unsetopt NOMATCH`, so zsh's `no matches found` error and most brace-expansion surprises are already fixed globally. Do not reach for `emulate` to "fix" those — they are already fixed.

## When

A `bash` tool invocation fails with a zsh-specific error that bash would not produce, **and the global unsetopt has not already addressed it**, and the command looks bash-portable. Common symptoms:

- `zsh: command not found: ...` for a construct that bash parses as a builtin (e.g. `[[ ... ]]` when you meant `[ ... ]`).
- `zsh: parse error near ...` near `((` arithmetic, here-string `<<<`, or process substitution `<(...)`.
- A pattern using bash-only glob semantics that zsh's extended glob misinterprets despite NOMATCH being unset.

## The fallback — what actually works

**`emulate -LR sh` does not do what its name suggests in zsh.** The `-L` flag in zsh means "local to the immediately surrounding shell function, if any" (see `man zshmisc` §"Shell Builtin Commands" → `emulate`). At the top level of an interactive session or of `bash -c '...'`, there is no surrounding function, so `-L` is silently ignored and the sh emulation **leaks into the persistent session** for the rest of the bash tool's lifetime — every subsequent `bash` invocation inherits NO_NOMATCH, KSH_ARRAYS, and POSIX_BUILTINS-adjacent behaviour until the session ends.

That is almost never what you want. Instead:

1. **For a single command**, run it under `bash -c '...'` so the sh emulation is scoped to the subshell and the surrounding zsh session is untouched:

   ```bash
   bash -c 'mv /etc/nginx/conf.d/*.conf /tmp/old-$(date +%F)/'
   ```

2. **For real bash semantics** (not just sh-shaped options), use `bash -c '...'` with `shellcheck -s sh` validation. `emulate sh` does not change zsh syntax (`[[ ]]`, `(( ))`, `<(...)`, parameter flags, zsh-only variables like `$ZSH_VERSION`); it only flips option flags. If you wrote zsh syntax and ran `emulate -LR sh` in front of it, the command breaks differently than the original failure.

3. **For a script** that must be portable, write it to a temp file with `#!/bin/sh` and run it. Do not lean on shell-emulation tricks to make a zsh-shaped script "act bash".

## Anti-patterns

- Prefix any command with `emulate -LR sh` "to be safe" — leaks sh emulation into the rest of the session and breaks zsh features you actually want.
- Reach for `emulate sh` when the real fix is a different **shell** — zsh's `**`, `(a|b)` extended glob, and `$array[(i)val]` look zsh-natural but break in bash too. If the script must be portable, use `find` / `case` / explicit loops, not simulation tricks.
- Add `emulate sh` to your interactive `.zshrc` — kills zsh features you'll want at the prompt. Per-command only.
- Try `unsetopt NOMATCH` "again" to fix a `no matches found` error — it is already unset at `dot_shell/zsh/00-before-zgenom.zsh:29`. If you see the error after that line ran, the regression is somewhere else.
