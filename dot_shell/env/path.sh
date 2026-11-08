# ~/.shell/env/path.sh
# The user-owned PATH entries. Sourced by ~/.zshenv, ~/.bashrc, and by every
# non-interactive bash through $BASH_ENV (set in
# ~/.config/environment.d/10-shell-env.conf).
#
# Keep this file POSIX sh. It also runs inside `bash -c`, so it must stay
# silent and must not assume an interactive shell.
#
# The helper directory comes first, the way the interactive zsh had it. It
# holds runpriv, and util-linux puts a different runpriv in /usr/bin, so
# the helper must stay ahead of the system directories. It also holds the
# managed pinentry-switch, and ~/.local/bin holds an old copy of it.
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

# Helper first: it must win over the system directories.
_helper="$HOME/.shell/helper"
case ":$PATH:" in
*":$_helper:"*) ;;              # already present, leave PATH alone
*) PATH="$_helper:$PATH" ;;     # prepend
esac
unset _helper

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
