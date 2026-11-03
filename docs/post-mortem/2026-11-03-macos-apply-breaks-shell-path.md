---
severity: high
status: open
date: 2026-11-03
owner: the dotfiles maintainer
---

# The macOS apply deployed a broken PATH — post-mortem

## Summary

The `chezmoi apply` on 2026-11-03 deployed `dot_shell/zsh/10-common-export.zsh`
to the macOS work laptop. One line in that file built PATH with a quoted
array inside an assignment. zsh collapses that into a single element, so
PATH held one directory entry of 1071 bytes. macOS rejects any command
candidate path longer than PATH_MAX, which is 1024 bytes on this host.
Every lookup of an external command returned ENAMETOOLONG, so a new shell
could run nothing.

Two more defects sat behind the first one. The PATH had no deduplication,
so it grew by one fnm multishell directory per shell generation. And the
repo's `dot_zprofile` does not run `brew shellenv`, so `python3` resolved
to the system Python 3.9 while the shellx helper needs 3.10 or newer. The
apply replaced the live `.zprofile` with the repo version, which removed
the only call to `brew shellenv` on this host.

The shell was fixed 13 minutes after the apply. The follow-up items in the
table at the end of this document are still open.

## Detection

The user opened a new zsh and pasted its output. No alert, no test and no
log reported the failure. The shell printed it at startup:

```text
/Users/muhamad.ardhinata/.shell/zsh/10-common-export.zsh:51: file name too long: opencode
/Users/muhamad.ardhinata/.shell/zsh/12-gpg.zsh:22: file name too long: gpgconf
execvP: /Users/muhamad.ardhinata/.shell/helper /Users/muhamad.ardhinata/.local/state/fnm_multishells/73140_1793711281256/bin /usr/local/bin /System/Cryptexes/App/usr/bin /usr/bin /bin /usr/sbin /sbin … : path too long
env: python3: No such file or directory
shellx: warning: failed to load OPENROUTER_API_OPENCODE_INDEX (exit 127)
__zgenom_autoupdate_background:16: file name too long: git
```

The `execvP` line shows the whole fault in one place. The PATH held 27
colon-separated entries. It appears as one space-separated entry. That
single entry is 1071 bytes long.

## Timeline

All times are local time on the work laptop, UTC+0700.

| Time | Event |
|---|---|
| 2026-11-03 09:07 | Commit `f855bab` lands. The macOS portability change adds the JetBrains Toolbox block to `dot_shell/zsh/10-common-export.zsh`, including the line `path=("$path" "$_jb_scripts")`. No test covers the file. |
| 2026-11-03 09:29 | Commit `5e62a4a`, the last repo commit before the apply. |
| 2026-11-03 20:07 | `chezmoi apply` deploys `~/.zshrc` and `~/.zprofile` as plain files, replacing the symlinks into the live `~/.shell/` layout. It also deploys the zsh snippets into `~/.shell/zsh/`. |
| 2026-11-03 20:07 | The first new shell after the apply fails. The user reports the output above. |
| 2026-11-03 20:15 | The array fix and the PATH hygiene reach `~/.shell/zsh/10-common-export.zsh`. |
| 2026-11-03 20:20 | `brew shellenv` reaches `~/.shell/zsh/00-before-zgenom.zsh`. The shell runs commands again. |
| 2026-11-03 20:2x | `shellx init` creates the store, and the OpenRouter key is restored into it. |

## Root cause

Three contributing causes, most significant first.

### 1. A quoted array inside an assignment

`dot_shell/zsh/10-common-export.zsh` added the JetBrains Toolbox scripts
directory like this:

```zsh
path=("$path" "$_jb_scripts")
```

In zsh, `"$path"` inside double quotes joins the array elements with a
space and yields one word. The assignment therefore sets `path` to a
two-element array. The first element is the whole old PATH, with spaces
in place of colons. `PATH` is tied to `path`, so PATH becomes that value.

zsh then searches one directory, whose name is 1071 bytes. macOS rejects
any candidate path longer than PATH_MAX, which is 1024 bytes on this
host. The candidate is that entry plus a slash plus the command name, so
every lookup of an external command returns ENAMETOOLONG. zsh reports it
as `file name too long: <command>`.

The correct form is `path+=("$_jb_scripts")`, which appends one element.

The collapse breaks the lookup on every host, not only on macOS. The
macOS part is the error message. On this host a single element of 1071
bytes exceeds PATH_MAX, so the candidate path fails the length check.
On a host with a larger limit, the lookup still fails, because no
directory carries that name.

### 2. No PATH hygiene

`fnm env --use-on-cd` prepends one multishell directory per shell
generation. Each shell inherits the PATH of its parent. Nothing removed
the parent shells' directory, and nothing deduplicated the result. The
user's PATH carried 27 entries: two fnm multishell directories,
`.local/bin` three times and `.bun/bin` twice.

The length was not the problem on its own. A PATH of 3001 bytes with
short elements still resolves on this host, because macOS limits the
candidate path and not the total PATH. The collapse turned a 1071-byte
total into one 1071-byte element, which crossed PATH_MAX by 47 bytes.
The two defects combined.

### 3. `brew shellenv` was missing from the repo

The live `~/.shell/.zprofile` ran `brew shellenv`. The repo's
`dot_zprofile` does not. macOS `/etc/zprofile` runs `path_helper`, which
leaves `/usr/bin` ahead of `/opt/homebrew/bin`. So `python3` resolved to
the system Python 3.9.6, and the shellx helper failed with:

```text
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

The helper uses `X | None` annotations, which need Python 3.10 or newer.
The apply replaced the live `.zprofile` with the repo version, so the
only call to `brew shellenv` on this host disappeared.

## Impact

| Measure | Value |
|---|---|
| Hosts affected | 1, the macOS work laptop |
| Duration | 13 minutes, from the apply at 20:07 to the fix at 20:20 |
| Shells affected | Every new interactive zsh |
| Commands affected | Every external command. Only zsh builtins ran. |
| Data loss | None |
| Sessions blocked | OpenCode, AFT and the magic-context tooling, because the shellx helper could not load `OPENROUTER_API_OPENCODE_INDEX` |

The fault sat in the source tree, so any host that ran the same apply
with the same config had it. The Linux host had not taken this commit.

## Resolution

Four changes, all in the source tree and all deployed to this host.

1. `dot_shell/zsh/10-common-export.zsh` now appends with
   `path+=("$_jb_scripts")` instead of assigning a quoted array.
2. The same file now sets PATH hygiene at the top. `typeset -U path`
   removes duplicates and keeps the first occurrence, and
   `path=(${path:#*/fnm_multishells/*})` drops the parent shells' fnm
   directories. The file adds the one multishell directory for the
   current shell further down.
3. `dot_shell/zsh/00-before-zgenom.zsh` now runs `brew shellenv`. It
   runs before Prezto's `compinit`, so the Homebrew completions still
   register.
4. `shellx init` created the store. The OpenRouter key went into it from
   the live `~/.shell/.zshrc`. That file survives the apply, because
   chezmoi does not manage it.

The state after the fix:

```text
PATH=24 entries, 984 bytes
python3=Python 3.15.2
OPENROUTER_API_OPENCODE_INDEX set
command -v ls resolves in a login shell
chezmoi apply --dry-run --force → exit 0
```

## Action items

| Action item | Type | Priority | Owner | Tracking |
|---|---|---|---|---|
| Add a startup check that runs `zsh -lic 'command -v ls'` and fails when the lookup fails | detect | P1 | the dotfiles maintainer | this document |
| Add a test that asserts the count of `path` elements equals the count of PATH entries | prevent | P1 | the dotfiles maintainer | this document |
| Guard `brew shellenv` per platform in the zsh stack | prevent | P2 | the dotfiles maintainer | this document |
| Move the nine remaining `~/.shell/useropts/` rows into `dot_shell/zsh/` | prevent | P1 | the dotfiles maintainer | `.agents/docs/macos-apply-blockers.md` |
| Restore the signing keys `330FE76C4FD0F3BC` and `9909A0802A11B93F` | mitigate | P2 | the user | `.agents/docs/macos-apply-blockers.md` |

## Lessons learned

- **A quoted array inside an assignment is not an append in zsh.**
  `path+=("...")` is. The same mistake breaks any array, not only PATH.
- **macOS limits the candidate path, not the total PATH.** A 3001-byte
  PATH with short elements resolves. Only the collapse made the length
  fatal.
- **A portability commit is the riskiest place for a latent bug.** The
  line sat in the repo for hours and then broke every shell on the host.
- **The audit measured the targets, not the effective environment.** The
  pre-apply audit listed all 53 changed targets and checked the SSH
  hazards. It did not compare the resolved PATH or the resolved `python3`
  between the live shell and the repo shell.
- **One failure hid the next.** The ENAMETOOLONG error masked the Python
  version fault and the shellx warning. Each one surfaced only after the
  previous one cleared.
- **The error message names the symptom, not the cause.** `file name too
  long` points at the length. The cause was an array assignment.

## See also

- `.agents/docs/macos-apply-fixed.md` — the defects the apply exposed,
  with the fix for each one
- `.agents/docs/macos-apply-blockers.md` — the six blockers, and the
  items that are still open
- `docs/reports/2026-11-03-macos-apply-audit/` — the audit that ran
  before the apply
- `docs/reports/2026-11-03-macos-host-portability.md` — the source-state
  change that introduced the faulty line
