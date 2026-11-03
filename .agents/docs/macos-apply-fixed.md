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
