zgenom_refresh_cache() {
	# Delete all compiled zwc and do zgenom reset
	if (( ${+functions[zgenom]} == 0 )); then
		echo "zgenom_refresh_cache: zgenom is not loaded" >&2
		return 1
	fi
	find "${SHELL_TOOL_DIR}" -maxdepth 1 -type f -iname "*.zwc" -delete 2>/dev/null
	find "${HOME}" -maxdepth 1 -type f -iname ".z*.zwc" -delete 2>/dev/null
	rm -f "${XDG_CACHE_HOME:-$HOME/.cache}/prezto/zcompdump"
	zgenom reset
}
