# zsh-stack Router

Load the `zsh-stack` skill before working on this project's zsh configuration stack. The skill captures the tunables, pitfalls, and project-specific quirks that you would otherwise rediscover (or repeat).

## Load the `zsh-stack` skill when any of these is true

- About to edit `dot_zshrc`, `dot_shell/zsh/*`, `dot_zprofile`, `dot_zshenv`, or `dot_p10k.zsh`.
- User mentions `zgenom`, `prezto`, `powerlevel10k`, `p10k`, `pmodload`, `compinit`, `zcompdump`, `.zwc`, `instant prompt`, `prompt_substring_search`, `UPDATESTARTUPTTY`, or `gpg-agent` in a zsh context.
- Debugging slow zsh startup, broken completions, missing prompt segments, stale `.zwc` bytecode, or pinentry opening on the wrong tty.
- Adding/removing a prezto module, changing a module's `zstyle`, or reordering the prezto module list.
- User asks about zsh performance, prompt customization, completion caching, or the gpg-agent/TTY lifecycle in a shell context.

## Why a router

The `zsh-stack` skill is dense (~400 lines) — it covers three interdependent projects (zgenom, prezto, p10k) with their own tunables, APIs, and footguns. Loading it eagerly ensures the agent doesn't:

- Reverse the prezto module load order (env → completion → syntax-highlighting → history-substring-search → prompt is load-bearing).
- Forget to disable the prezto `gpg` module via the `loaded` zstyle before zgenom init.
- Recursively compile `$SHELL_TOOL_DIR` and end up with stale `.zwc` bytecode shadowing source edits.
- Run `p10k configure` and overwrite the chezmoi-managed `dot_p10k.zsh`.
- Read the GPG_TTY value at `.zshrc` source time and leak a stale value into the systemd --user manager env (alacritty reassigns the controlling tty mid-startup).

The router keeps the rule file short and lets the skill own the full reference.