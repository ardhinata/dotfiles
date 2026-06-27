# ~/.shell/zsh/10-common-export.zsh
# Common shell exports and aliases. Sourced by ~/.zshrc after zgenom/Prezto
# initialization, so the completion system is already active.
# SHELL_TOOL_DIR is defined in ~/.zshrc as ${HOME}/.shell.

# --- Editor preference ---
# Set EDITOR to the first available editor from the ordered preference list.
if [[ -n $(which nvim) ]]; then
	export EDITOR=nvim
elif [[ -n $(which vim) ]]; then
	export EDITOR=vim
elif [[ -n $(which nano) ]]; then
	export EDITOR=nano
fi

# --- GPG-based SSH agent ---
# Use GnuPG's SSH agent socket instead of the system ssh-agent.
# updatestartuptty tells gpg-agent about the current TTY for pinentry.
if [[ -n $(gpgconf --list-dirs agent-ssh-socket) ]]; then
	export SSH_AUTH_SOCK="$(gpgconf --list-dirs agent-ssh-socket)"
	gpg-connect-agent updatestartuptty /bye >/dev/null
fi

# --- Fast Node Manager ---
# Initialize fnm in the shell session, respecting .node-version and .nvmrc files
# when changing directories (--use-on-cd).
eval "$(fnm env --use-on-cd --shell zsh)"

# --- runpriv: privileged process launcher ---
# runpriv injects decrypted environment tokens from the per-profile JSON store
# into a target process. Available on PATH via ~/.shell/helper.
path=("${SHELL_TOOL_DIR}/helper" $path)
# Completion is handled by ~/.shell/zsh/completions/_runpriv,
# loaded via fpath (set in 00-before-zgenom.zsh before compinit runs).
