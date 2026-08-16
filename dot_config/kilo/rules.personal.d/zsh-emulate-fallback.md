# Bash Tool — zsh Emulation Fallback

The `bash` tool runs each command inside this zsh session. zsh and bash default
to different behavior for some shell constructs even when the script "looks
the same." Most no-match and brace-expansion cases are fixed globally in
`dot_shell/zsh/00-before-zgenom.zsh` (`unsetopt NOMATCH`). Use this fallback
when **a bash-style script still errors or misbehaves** despite that global
flip.

## When

A `bash` tool invocation fails with a zsh-specific error that bash would not
produce, and the command looks bash-portable. Common symptoms:

- `no matches found: <pattern>` after an `unsetopt NOMATCH` regression, or a
  pattern that uses `**`, `~`, `^`, or `#` (zsh extended glob, no bash analog).
- `zsh: command not found: ...` for a construct that bash parses as a builtin
  (e.g. `[[ ... ]]` when you meant `[ ... ]`).
- `zsh: parse error near ...` near `((` arithmetic, here-string `<<<`, or
  process substitution `<(...)`.

## The fallback

Prefix the failing command with `emulate -LR sh` — **once per command**, not
once per session. `-L` keeps the options local to that command, `-R` resets
all settable options to the sh baseline, and `sh` tunes for bash-like
behavior (POSIX_BUILTINS-adjacent, sets NO_NOMATCH + KSH_ARRAYS, disables
zsh-specific pattern syntaxes):

```bash
emulate -LR sh; mv /etc/nginx/conf.d/*.conf /tmp/old-$(date +%F)/
```

Reach for the fallback only after confirming the command is bash-shaped. If
you intentionally wrote zsh syntax (`${(s/,)var}`, `[[ ]],  zmv`, etc.), the
fallback will break it — that's the point, revert and don't use the prefix.

## Why not the primary fix

`emulate -LR sh` is **not** equivalent to running under bash:

- It does not change zsh **syntax** — `[[ ]]`, `(( ))`, `<(...)`, here-strings,
  zsh-only parameter flags all still parse as zsh.
- It sets zsh-specific **options** only (NO_NOMATCH, KSH_ARRAYS, SH_GLOB,
  NO_BARE_GLOB_QUAL, BSD_ECHO, …). Builtins like `echo`, `printf`, `getopts`,
  `read`, `time` still behave like zsh.
- It silently keeps zsh-only **variables** loaded (`$RANDOM`, `$ZSH_VERSION`,
  `$ZSH_NAME`, …).

For real bash semantics, the honest tool is `bash -c '...'` or a `#!/bin/sh`
shebang with `shellcheck -s sh` validation — not a session-side emulation.
This rule is the escape hatch for the **bash-tool sessions only**, where
those heavier mechanisms are impractical.

## Anti-patterns

- Adding `emulate sh` to your interactive `.zshrc` — kills zsh features
  you'll actually want at the prompt. Per-command fallback only.
- Wrapping every command in `emulate -LR sh` "to be safe" — adds noise and
  occasional syntax breakage. Try without first.
- Reaching for `emulate sh` when the real fix is a different **shell**:
  zsh's `**`, `(a|b)` extended glob, and `$array[(i)val]` look zsh-natural
  but break in bash too. If the script must be portable, use `find` /
  `case` / explicit loops, not simulation tricks.

## References

- `dot_shell/zsh/00-before-zgenom.zsh` — the source of the persistent
  `unsetopt NOMATCH` that solves the most common no-match class of bugs.
- zsh docs `man zshbuiltins` → `emulate` — full semantics of `-L` / `-R` /
  per-shell baseline, including the unavoidable parts `emulate sh` does not
  fix.
