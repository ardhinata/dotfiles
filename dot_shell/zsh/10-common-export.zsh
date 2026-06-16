# Check editor path and set editor by order of preference.
if [[ -n $(which nvim) ]]; then
	export EDITOR=nvim
elif [[ -n $(which vim) ]]; then
	export EDITOR=vim
elif [[ -n $(which nano) ]]; then
	export EDITOR=nano
fi

if [[ -n $(gpgconf --list-dirs agent-ssh-socket) ]]; then
	export SSH_AUTH_SOCK="$(gpgconf --list-dirs agent-ssh-socket)"
	gpg-connect-agent updatestartuptty /bye >/dev/null
fi

alias runpriv="$SHELL_TOOL_DIR/helper/runpriv.sh"
