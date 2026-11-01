# ~/.shell/zsh/20-secret-env-load.zsh
# Load shell-wide secret environment variables from the shellx store.
#
# `shellx env NAME` decrypts one variable and prints one `export NAME=<value>`
# line. The helper quotes the value, so it stays one word.
#
# The helper decrypts on every shell start. The master key comes from
# ~/.local/share/shellx/master.key, which `chezmoi apply` renders.
#
# A failure prints a warning on stderr and leaves the variable unset. The
# shell still starts: a missing secret must not block the login.

if [[ -x "${SHELL_TOOL_DIR}/helper/shellx" ]]; then
	_shellx_env_load() {
		local _line _rc _xtrace=0
		# Turn off xtrace so the secret never reaches a trace log.
		[[ -o xtrace ]] && { _xtrace=1; set +x; }
		_line="$("${SHELL_TOOL_DIR}/helper/shellx" env "$1")"
		_rc=$?
		if (( _rc == 0 )); then
			eval "$_line"
		else
			# The helper already printed the reason on stderr.
			print -u2 "shellx: warning: failed to load $1 (exit $_rc)"
		fi
		(( _xtrace )) && set -x
		return 0
	}
	_shellx_env_load OPENROUTER_API_OPENCODE_INDEX
	unset -f _shellx_env_load
else
	print -u2 "shellx: warning: helper not found at ${SHELL_TOOL_DIR}/helper/shellx"
fi
