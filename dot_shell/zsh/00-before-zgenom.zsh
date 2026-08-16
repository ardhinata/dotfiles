# ~/.shell/zsh/00-before-zgenom.zsh
# Runs before zgenom/Prezto initialization in ~/.zshrc.
# SHELL_TOOL_DIR is set in ~/.zshrc before this file is sourced.

# Register custom completions directory so Prezto's completion module
# discovers completions (e.g. _runpriv via #compdef) during compinit.
fpath=("${SHELL_TOOL_DIR}/zsh/completions" $fpath)

# Skip Prezto's gpg module. Its `init.zsh` does `export GPG_TTY=$TTY` at
# pmodload time, but $TTY at that moment is not yet the controlling tty we
# want — it leaks a stale value that then survives into the agent's
# import-environment and points pinentry at the wrong alacritty tab on the
# next SSH sign attempt. We replicate the only useful bit (the preexec
# UPDATESTARTUPTTY hook) in 10-common-export.zsh and own GPG_TTY ourselves.
# Prezto's documented disable mechanism (see pmodload in prezto/init.zsh):
#   if zstyle -t ":prezto:module:$pmodule" loaded 'yes' 'no'; then continue
zstyle ':prezto:module:gpg' loaded 'yes'

# Align default glob-no-match behavior with bash for the bash tool.
# zsh's NOMATCH option (on by default) errors out with "no matches found: ..."
# when a pattern like `*.log` finds no matching files. bash and most shell
# scripts preserve the literal pattern in that case, which is what the bash
# tool's caller expects when running bash-style one-liners. Disabling NOMATCH
# here makes both interactive zsh and the persistent bash-tool session
# (which runs in this same zsh instance) behave like bash for glob defaults.
# This does NOT touch syntax (`[[ ]]`, process substitution, arrays) or
# builtins — see ~/.config/kilo/rules.personal.d/zsh-emulate-fallback.md
# for the per-command `emulate -LR sh` escape when those diverge.
unsetopt NOMATCH
