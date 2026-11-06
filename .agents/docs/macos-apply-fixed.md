# macOS apply findings that are already fixed

The defects the apply exposed on the macOS work laptop, and the fix for each
one.

Companion to [`macos-apply-blockers.md`](macos-apply-blockers.md), which
holds the open blockers, and
[`macos-apply-caveats.md`](macos-apply-caveats.md), which holds the changes
that do not block the apply.

The PATH collapse has a full post-mortem at
[`docs/post-mortem/2026-11-03-macos-apply-breaks-shell-path.md`](../../docs/post-mortem/2026-11-03-macos-apply-breaks-shell-path.md).

All findings were verified on 2026-11-03 with chezmoi v2.74.0 against the
live host.

## The PATH collapsed after the apply

`dot_shell/zsh/10-common-export.zsh` added the JetBrains Toolbox scripts
with `path=("$path" "$_jb_scripts")`. In zsh, a quoted array inside an
assignment joins the elements with a space and keeps them as one word.
The whole PATH became a single 3000-byte path element, so every command
lookup failed:

```
execvP: /Users/…/.shell/helper /Users/…/fnm_multishells/…/bin …: path too long
```

The line is now `path+=("$_jb_scripts")`. The bug came in with commit
`f855bab` and stayed invisible until the apply deployed the file.

Two PATH hygiene steps were added next to it:

- `typeset -U path` removes duplicate directories. The old file added
  `~/.local/bin` and `~/.bun/bin` on every shell start, and each one
  was already on the PATH.
- `path=(${path:#*/fnm_multishells/*})` drops the fnm multishell
  directory of the parent shell. `fnm env` adds one for the current
  shell. Every shell inherited the one of its parent, so the PATH grew by
  about 63 bytes per shell generation. The host carried 25 of them.

After the fix the PATH has 24 entries and is 984 bytes long.

## `brew shellenv` runs again

The live `~/.shell/.zprofile` ran `eval "$(/opt/homebrew/bin/brew shellenv
zsh)"`. The repo `dot_zprofile` does not, so the Homebrew prefix lost
its place in the PATH.

macOS `/etc/zprofile` runs `path_helper`, which leaves `/usr/bin` ahead
of `/opt/homebrew/bin`. Without `brew shellenv`, `python3` resolved to
the system Python 3.9, and the shellx helper needs Python 3.10 or
newer:

```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

`dot_shell/zsh/00-before-zgenom.zsh` now runs `brew shellenv`. It runs
before Prezto's `compinit`, so the Homebrew completions in
`/opt/homebrew/share/zsh/site-functions` are picked up. It costs about
40 ms per shell start.

## The Homebrew opts are back in

Restored on 2026-11-06 in `dot_shell/zsh/05-homebrew-opts.zsh`
(darwin-gated, sourced from `dot_zshrc.tmpl` right after
`00-before-zgenom.zsh`), from the orphaned pre-apply files backed up at
`~/.local/state/chezmoi-host-artifacts/shell/`. It carries the
verbatim content of `00-brew-fix.zsh` (the awscli
`DYLD_LIBRARY_PATH` expat patch and the brew `python` `libexec/bin`
entry on PATH, appended with `path+=`) plus the
`HOMEBREW_CASK_OPTS="--appdir=~/Applications"` export that sat directly
in `~/.shell/.zshrc`. Verified in a fresh zsh: `DYLD_LIBRARY_PATH` is
`/opt/homebrew/opt/expat/lib`, the cask opts render verbatim, and
`/opt/homebrew/opt/python@3.15/libexec/bin` lands on `$path`.

Still open from the same useropts directory (owner: the user, to do
when there is time): openblas `LDFLAGS`/`CPPFLAGS`/`PKG_CONFIG_PATH`,
SDKMAN init, `BUN_INSTALL`/bun completions, and the opencode
completions. They are also gated out on non-darwin if ported, and the
SDKMAN file would need to stay last. See
[`macos-apply-blockers.md`](macos-apply-blockers.md) for the row state.

## The shellx helper had no Python 3.10 interpreter

Fixed by the `brew shellenv` change above. `python3` is now
`/opt/homebrew/bin/python3`, which is Python 3.15. The helper keeps its
documented requirement of Python 3.10 or newer.

## `check_decrypt.sh` mapped the wrong target path

`.shell_helper/check_decrypt.sh` mapped the source-state attributes on the
file name only, so `dot_shell/private_store/` mapped to
`.shell/private_store/...` instead of `.shell/store/...`. The encrypted
store escaped the ignore rule and the apply failed on it. The mapping is
now rewritten to strip the attributes that apply to each component, in
chezmoi's parse order.

Verified against `chezmoi target-path` for all 25 encrypted files plus 228
attribute combinations. Run `bash .shell_helper/test_check_decrypt.sh` to
confirm the mapping still matches.


## `~/Work` lost the git identity override

Documented in `macos-apply-caveats.md` before the apply and left open since:
the repo `dot_gitconfig` includes `~/Work/.gitconfig`, a host-local file
that existed on neither host, and the pre-apply laptop config instead
included `~/Work/local/.git_local` under `gitdir:~/Work/local/`. After the
apply every repo under `~/Work` committed with the personal identity and
nothing was gpg-signed. Verified 2026-11-05: apply backup
`~/.local/state/chezmoi-backup-final/files/.gitconfig` (the pre-apply
config), and the work and personal signing subkeys
(`0x32A87E6BED04FEC6`, `0x17A0476897A8A861`) both in the local keyring.

Fixed 2026-11-05 by creating `~/Work/.gitconfig` (host-local, not managed
by chezmoi, kept out of the repo): work identity for `~/Work`
(`Muhamad Ardhinata J.`, `muhamad.ardhinata@krom.id`, key `0x32A87E6B`,
`gpgSign = yes`) plus a nested `includeIf "gitdir:~/Work/local/"` to
`~/Work/local/.git_local`. Global config and other paths keep the applied
repo identity. `git config --get --show-origin` confirms: work repos
under `~/Work` resolve to the work identity, a repo under
`~/Work/local` to the personal `.git_local` identity with
`commit.gpgsign` inherited from the work include, and anything outside
`~/Work` to the repo template values.
