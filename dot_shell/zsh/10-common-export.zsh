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

# --- Local executable dir ---
export PATH="${PATH}:${HOME}/.local/bin"

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

# --- kilo wrappers (shared-context CLI merged into kilo-shared) ---
# Deployed by .agents/kilo/setup-script at Agent Manager worktree creation.
# Adds ~/.local/share/kilo/bin (kilo-shared, kilo-helper-shared-detect,
# kilo-shared-init.sh) to PATH when the dir exists. Idempotent — no-op on
# fresh machines before any Agent Manager worktree setup.
if [ -d "${HOME}/.local/share/kilo/bin" ]; then
  path=("${HOME}/.local/share/kilo/bin" $path)
fi
