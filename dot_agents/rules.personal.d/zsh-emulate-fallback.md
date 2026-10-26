# Bash Tool — zsh Emulation Fallback

The shell tool runs each command as `<shell> -c "<command>"`: a fresh,
non-interactive, non-login shell. It loads no rc file. There are no aliases,
no `setopt`, and no `shopt` from the interactive session.

This host pins `"shell": "/usr/bin/bash"`, so tool commands run in bash. Check
with one call when it matters:

```sh
echo "$0"; echo "${BASH_VERSION:-no-bash}${ZSH_VERSION:-no-zsh}"
```

If a command fails with a zsh-specific error, run it under `bash -c '...'`
so the shell semantics stay inside the subshell. Do not use `emulate -LR sh`:
at the top level the `-L` flag is ignored, and the sh emulation leaks into
the rest of the session.
