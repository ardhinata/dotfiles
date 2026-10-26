# zsh-stack Hazards

Load the `zsh-stack` skill before you touch this project's zsh configuration
stack. The skill is the full reference. These hazards cost the most when
missed:

- Never run `p10k configure`. It overwrites the chezmoi-managed
  `dot_p10k.zsh`.
- The prezto module load order is load-bearing: env → completion →
  syntax-highlighting → history-substring-search → prompt.
- Disable the prezto `gpg` module through the `loaded` zstyle before zgenom
  init.
- Do not recursively compile `$SHELL_TOOL_DIR`. Stale `.zwc` bytecode shadows
  source edits.
- Do not read `GPG_TTY` at `.zshrc` source time. It leaks a stale tty into
  the systemd --user manager env.
