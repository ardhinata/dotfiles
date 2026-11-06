# ~/.shell/zsh/05-homebrew-opts.zsh
# macOS Homebrew opts that lived in the orphaned ~/.shell/useropts/
# before the 2026-11-03 apply: the HOMEBREW_CASK_OPTS export of
# ~/.shell/.zshrc and the expat/python fixes of 00-brew-fix.zsh, carried
# over near-verbatim. The rest of that directory (openblas flags,
# SDKMAN, bun, opencode completions) is NOT ported; the backup is at
# ~/.local/state/chezmoi-host-artifacts/shell/useropts.tar.

if [[ $OSTYPE == darwin* ]]; then

	# Casks install to ~/Applications, not /Applications. Kept verbatim
	# from the pre-apply ~/.shell/.zshrc; brew resolves the ~ itself.
	export HOMEBREW_CASK_OPTS="--appdir=~/Applications"

	# Resolve brew lib path
	_brew_lib_path() {
		local paths=()
		for lib in "$@"; do
			local p
			p=$(brew --prefix "$lib" 2>/dev/null)
			[[ -n "$p" ]] && paths+=("$p/lib")
		done
		print -r -- "${(j.:.)paths}"
	}

	# Patch for awscli error expecting newer expat lib
	export DYLD_LIBRARY_PATH="$(_brew_lib_path expat)${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"

	# Add brew-specific libexec to $PATH
	_brew_libexec_path() {
		local paths=()
		for libexec_path in "$@"; do
			local p
			p=$(brew --prefix "$libexec_path" 2>/dev/null)
			[[ -n "$p" ]] && paths+=("$p/libexec")
		done
		print -r -- "${(j.:.)paths}"
	}
	_brew_lp=$(_brew_libexec_path python)
	[[ -n "$_brew_lp" ]] && path+=("$_brew_lp/bin")
	unset _brew_lp
fi
