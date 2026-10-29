# Shell Tool — zsh Emulation Fallback — OpenCode

OpenCode facts for the shared rule
`~/.agents/rules.personal.d/zsh-emulate-fallback.md`.

- The shell tool runs each command as `<shell> -c "<command>"`: a fresh,
  non-interactive, non-login shell. It loads no rc file, and it has no
  aliases and no `setopt` or `shopt` from the interactive session.
- The `shell` key in `~/.config/opencode/opencode.jsonc` picks the binary.
  This host pins it to `/usr/bin/bash`, so tool commands run in bash.
- The shell tool's pty mode is `shell({ pty: true })`.
