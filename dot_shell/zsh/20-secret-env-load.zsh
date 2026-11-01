# ~/.shell/zsh/20-secret-env-load.zsh
# Load shell-wide secret environment variables from the shellx store.
#
# `shellx env NAME` decrypts one variable and prints one `export NAME=<value>`
# line. The helper quotes the value, so it stays one word.
#
# The helper decrypts on every shell start. One variable costs about 115 ms:
# 65 ms of helper start plus the scrypt key derivation. Keep this list short.
#
# A failure prints to stderr and leaves the variable unset. The status check
# turns the failure into a message instead of a silent empty export.

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
			print -u2 "shellx: failed to load $1"
		fi
		(( _xtrace )) && set -x
		return _rc
	}
	_shellx_env_load OPENROUTER_API_OPENCODE_INDEX
	unset -f _shellx_env_load
fi
