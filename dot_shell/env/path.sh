# ~/.shell/env/path.sh
# The user-owned PATH entries. Sourced by ~/.zshenv and ~/.bashrc, and by
# every non-interactive bash on Linux through $BASH_ENV (set in
# ~/.config/environment.d/10-shell-env.conf). macOS has no systemd, so the
# BASH_ENV path does not run there.
#
# Keep this file POSIX sh. It also runs inside `bash -c`, so it must stay
# silent and must not assume an interactive shell.
#
# The helper directory goes ahead of the system directories. It holds
# runpriv, and util-linux puts a different runpriv in /usr/bin, so the
# helper must stay ahead of them. It also holds the managed
# pinentry-switch, and ~/.local/bin holds an old copy of it. An interactive
# shell lists a few user directories before it, because the interactive
# startup prepends them after this file has run.
#
# On macOS /etc/zprofile runs path_helper after ~/.zshenv, and path_helper
# rewrites PATH with the system list first. An entry that is only added
# stays behind /usr/bin, so the helper and the Homebrew prefix are moved
# to the front instead of only being added.
#
# A missing directory is harmless. The shell skips it, and the entry starts
# to work as soon as the directory appears. Do not test for the directory
# here: a skipped entry stays missing for the whole shell session.
#
# The system directories (/usr/local/bin, /usr/bin, ...) are not listed.
# Every shell inherits them, and the systemd user manager exports them too.
# The dynamic entries (fnm, the Toolbox scripts) are not listed either: they
# belong to ~/.shell/zsh/10-common-export.zsh, which runs for interactive
# shells only.

# An unset PATH would make the entries below start with a colon, and a
# leading colon puts the current directory on PATH.
[ -n "${PATH:-}" ] || PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# Move one entry to the front of PATH. A parameter expansion cannot remove
# one element from the middle of PATH, so the loop peels the first element
# off the rest. It needs no word splitting, so it behaves the same in sh,
# bash and zsh.
_path_front() {
	_pf_new="$1"
	_pf_rest="$PATH"
	while [ -n "$_pf_rest" ]; do
		case "$_pf_rest" in
		*:*) _pf_e="${_pf_rest%%:*}"; _pf_rest="${_pf_rest#*:}" ;;
		*) _pf_e="$_pf_rest"; _pf_rest="" ;;
		esac
		[ -n "$_pf_e" ] || continue
		[ "$_pf_e" = "$1" ] || _pf_new="$_pf_new:$_pf_e"
	done
	PATH="$_pf_new"
	unset _pf_new _pf_rest _pf_e
}

# Homebrew first on macOS: /usr/bin/python3 is 3.9 and the shellx helper
# needs 3.10 or newer. The helper starts with /usr/bin/env python3, so the
# Homebrew prefix has to come before /usr/bin.
if [ "$(uname -s 2>/dev/null)" = Darwin ]; then
	for _brew_prefix in /opt/homebrew /usr/local; do
		if [ -x "$_brew_prefix/bin/brew" ]; then
			_path_front "$_brew_prefix/sbin"
			_path_front "$_brew_prefix/bin"
			break
		fi
	done
	unset _brew_prefix
fi

# Helper first: it must win over the system directories.
_path_front "$HOME/.shell/helper"

# User binaries last: they must not shadow a system binary.
for _p in \
	"$HOME/.local/bin" \
	"$HOME/.bun/bin" \
	"$HOME/go/bin"; do
	case ":$PATH:" in
	*":$_p:"*) ;;              # already present, leave PATH alone
	*) PATH="$PATH:$_p" ;;     # append
	esac
done
unset _p
export PATH
