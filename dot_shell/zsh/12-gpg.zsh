# ~/.shell/zsh/12-gpg.zsh
# Owns the GnuPG agent lifecycle for interactive zsh shells.
# Sourced by ~/.zshrc after 10-common-export.zsh.
# SHELL_TOOL_DIR is defined in ~/.zshrc as ${HOME}/.shell.
#
# Why this file exists:
#   Prezto's gpg module (disabled via zstyle in 00-before-zgenom.zsh) used to
#   set GPG_TTY=$TTY at module-load time. Two problems with that:
#     1. Prezto also unconditionally loaded pmodload 'ssh' + a preexec hook,
#        plus PINENTRY_USER_DATA — none of which we want now that the pinentry
#        backend is owned by ~/.shell/helper/pinentry-wrapper.
#     2. `$TTY` and `$(tty)` both return the previous alacritty tab's pts
#        during .zshrc source; the correct one only stabilizes by prompt time.
#   The preexec hook below catches that race at the moment the user actually
#   types a command, when tty is guaranteed stable.

# --- Startup: point SSH_AUTH_SOCK at gpg-agent and seed GPG_TTY ---
#
# `tty -s` is silent (no stdout pollution); raw `tty` writes "not a tty" to
# stdout on failure, so gate the actual `tty` call. See gpg-agent(1) and T6478
# for why GPG_TTY must be in the agent's startup env.
if [[ -n $(gpgconf --list-dirs agent-ssh-socket) ]]; then
	export SSH_AUTH_SOCK="$(gpgconf --list-dirs agent-ssh-socket)"
	if tty -s >/dev/null 2>&1; then
		export GPG_TTY="$(tty 2>/dev/null)"
		systemctl --user import-environment GPG_TTY 2>/dev/null
	fi
	# Tells the agent the SSH-protocol startup tty (different from GPG_TTY
	# in the agent's env — this is what sshd forwards back to the local tty
	# when prompting).
	gpg-connect-agent updatestartuptty /bye >/dev/null
fi

# --- Preexec hook: fix GPG_TTY just-in-time ---
#
# Alacritty reassigns the controlling tty mid-shell-startup, so the value
# captured at .zshrc source time may not match the actual terminal the user
# is in. By the time they press Enter on a command, tty is stable. The hook
# detects a mismatch, propagates GPG_TTY to the systemd --user manager env,
# and forces gpg-agent to relaunch so it inherits the corrected env. systemd
# restarts the agent within a few ms; the SSH socket path is unchanged so
# ssh/gpg clients reconnect transparently.
#
# Concurrent shells: each shell has its own GPG_TTY + its own preexec. The
# shared resource is the agent + systemd --user manager env. import-environment
# is last-write-wins — which matches the "most recent terminal" intent. Two
# tabs racing the first command in each: whichever preexec fires last wins,
# and the agent restarts once. If a second ssh is mid-flight when a peer's
# preexec kills the agent, that ssh hits a dead socket and fails — this only
# happens on the first command in a new tab where the tty race triggered;
# after that it's a no-op.
if (( $+commands[gpg-connect-agent] )); then
	autoload -U add-zsh-hook 2>/dev/null

	_gpg_preexec_refresh_agent_env() {
		if ! tty -s >/dev/null 2>&1; then
			return 0
		fi
		local _t
		_t=$(tty 2>/dev/null)
		[[ -z "$_t" ]] && return 0
		if [[ "$_t" != "${GPG_TTY:-}" ]]; then
			export GPG_TTY="$_t"
			systemctl --user import-environment GPG_TTY 2>/dev/null
			gpgconf --kill gpg-agent 2>/dev/null
		fi
		gpg-connect-agent updatestartuptty /bye >/dev/null 2>&1
	}

	add-zsh-hook preexec _gpg_preexec_refresh_agent_env 2>/dev/null
fi
