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

# --- Bun directory ---
export BUN_INSTALL="${HOME}/.bun"

# --- Local executable dir ---
export PATH="${PATH}:${HOME}/.local/bin:${BUN_INSTALL}/bin"

# --- Fast Node Manager ---
# Initialize fnm in the shell session, respecting .node-version and .nvmrc files
# when changing directories (--use-on-cd).
eval "$(fnm env --use-on-cd --shell zsh)"

# --- Helper directory ---
# shellx injects decrypted environment tokens into a target process.
# Available on PATH via ~/.shell/helper.
path=("${SHELL_TOOL_DIR}/helper" $path)
# Completion is handled by ~/.shell/zsh/completions/_shellx,
# loaded via fpath (set in 00-before-zgenom.zsh before compinit runs).

# --- JetBrains Toolbox scripts ---
# The Toolbox ships launcher scripts (idea, webstorm, ...) that belong on
# PATH. The directory differs per OS: Linux keeps it under ~/.local/share,
# macOS under ~/Library/Application Support. Add whichever one exists.
# This lives in a .zshrc-sourced file, not in ~/.zprofile: ~/.zprofile is
# read by login shells only, so an interactive non-login shell never saw
# the Toolbox scripts there.
for _jb_scripts in \
	"${HOME}/.local/share/JetBrains/Toolbox/scripts" \
	"${HOME}/Library/Application Support/JetBrains/Toolbox/scripts"; do
	if [[ -d "$_jb_scripts" ]]; then
		path=("$path" "$_jb_scripts")
	fi
done
unset _jb_scripts

if [[ -n $(which opencode) ]]; then
	source <(opencode --completions zsh);
fi
