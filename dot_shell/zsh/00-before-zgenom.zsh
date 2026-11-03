# ~/.shell/zsh/00-before-zgenom.zsh
# Runs before zgenom/Prezto initialization in ~/.zshrc.
# SHELL_TOOL_DIR is set in ~/.zshrc before this file is sourced.

# --- Homebrew ---
# Put the Homebrew prefix first in the PATH. macOS /etc/zprofile runs
# path_helper, which leaves /usr/bin ahead of /opt/homebrew/bin. That
# makes `python3` resolve to the system Python 3.9, and the shellx helper
# needs Python 3.10 or newer. brew shellenv also sets HOMEBREW_PREFIX,
# HOMEBREW_CELLAR and HOMEBREW_REPOSITORY, and adds the Homebrew
# completions to fpath. It runs here, before Prezto's compinit, so the
# completions are picked up.
for _brew in /opt/homebrew/bin/brew /usr/local/bin/brew; do
	if [[ -x "$_brew" ]]; then
		eval "$("$_brew" shellenv zsh)"
		break
	fi
done
unset _brew

# Register custom completions directory so Prezto's completion module
# discovers completions (e.g. _shellx via #compdef) during compinit.
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
# here makes the interactive zsh behave like bash for glob defaults. The bash
# tool does not read this file: it runs a fresh non-interactive bash, where
# NOMATCH does not exist. This does NOT touch syntax (`[[ ]]`, process
# substitution, arrays) or builtins — see
# ~/.agents/rules.personal.d/zsh-emulate-fallback.md for the per-command
# `bash -c` escape when those diverge.
unsetopt NOMATCH
