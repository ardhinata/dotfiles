# Revision: check the findings and the design

This file reviews the plan at commit `32a8978` on host `IKM202300278`, on
2026-11-10. It re-ran the measurements that the plan depends on. It also
checked the design against the live source tree.

The direction holds. The findings stand, with one exception (F2). Two
corrections block the implementation: the `_path_front` loop fails in zsh,
and Phase 4 uses `chezmoi apply`, which the README bans. The rest are
smaller defects.

## Confirmed claims

| Claim | Verdict | Evidence |
|---|---|---|
| F1: the `~/.zshenv` symlink becomes a regular file | Confirmed | `~/.zshenv` is a symlink to `.shell/.zshenv` (mode `120755`). `chezmoi diff` shows the deletion, then a `100644` file |
| F2: the helper needs Python 3.10 or newer | Confirmed | `/usr/bin/python3` is 3.9.6, `/opt/homebrew/bin/python3` is 3.15.2. `shellx list` exits 0 on 3.15 and raises `TypeError: unsupported operand type(s) for \|: 'type' and 'NoneType'` on 3.9 |
| F2: a non-interactive shell is broken, not absent | Confirmed | Today `zsh -c 'command -v shellx'` exits 1. With the upstream `path.sh` it finds the helper and then crashes |
| F2: `path_helper` puts the helper behind `/usr/bin` | Confirmed | `/etc/zprofile` runs `/usr/libexec/path_helper`. `/etc/paths` lists `/usr/local/bin` and `/usr/bin` before the `/etc/paths.d` entries. `/opt/homebrew/bin` lands after `/usr/bin` |
| F3: `environment.d` has no consumer on macOS | Confirmed | `BASH_ENV` is unset. No live shell file sets it |
| F4: the live `~/.bashrc` holds host-local lines | Confirmed | The Kiro CLI line and the FastPath block are present. Neither is in `dot_bashrc`. `~/.fastpath/env` does not exist |
| F5: the live `cli.json` is a strict superset | Confirmed | The live file adds `session.image_preview`, `session.sidebar`, `session.markdown`, `session.permissions` and `diffs.wrap`, and no other key |
| F6: the context7 endpoint answers | Confirmed | `initialize` returns HTTP 200 with no key |
| F6: `disabled` is a valid MCP field | Confirmed | `Mcp.RemoteConfigEncoded` accepts `type`, `url` and `disabled` (`https://opencode.ai/config.json`) |
| F6: both Zed font families are installed | Confirmed | `FiraMonoNerdFont-*.otf` and `TerminessNerdFont-*.ttf` |
| The new plugin exists | Confirmed | `opencode-orchestrator` resolves to 2.0.21 on npm |
| The router resolves, warns and falls back | Confirmed | A throwaway source tree returned the `IKM202300278` profile, warned `unknown host ... using the default profile`, and returned the `_default` profile |
| `.chezmoitemplates/` is not deployed | Confirmed | `chezmoi --source <tmp> managed` listed only the probe file |
| `include ".chezmoitemplates/hosts.yaml"` resolves | Confirmed | `include` reads a path relative to the source directory |

F2 overstates one point. It says "an interactive login shell fails the
same way". It does not. `brew shellenv` in `dot_shell/zsh/00-before-zgenom.zsh`
puts Homebrew first for every interactive shell, so `python3` resolves to
3.15.2 and the helper works. Measured on the live home:
`zsh -lic 'command -v python3'` prints `/opt/homebrew/bin/python3`. A
simulated upstream tree gives the same result. The breakage affects
non-interactive shells only, because they do not read `~/.zshrc`.

## Blocker 1: `_path_front` fails in zsh

The design calls the loop POSIX and says it runs under `sh`, `bash` and
`zsh`. zsh does not split an unquoted expansion by default. So
`for _pf_e in $PATH` runs one time, with the whole PATH in `_pf_e`.

Measured with a controlled PATH, after two calls:

```text
sh, bash: /opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
zsh:      /opt/homebrew/bin:/opt/homebrew/bin:/usr/bin:/bin:/opt/homebrew/bin:/usr/sbin:/sbin
```

In zsh the loop duplicates the entry, and the old copy stays in the
middle. Login shells source the file twice, so the duplicate grows with
each shell generation. `typeset -U path` hides this in interactive
shells. A non-interactive login shell has no such cleanup.

Use a loop that peels the first element. It needs no word splitting, so it
is correct in every shell:

```sh
_path_front() {
	_pf_new="$1"
	_pf_rest="$PATH"
	while [ -n "$_pf_rest" ]; do
		case "$_pf_rest" in
		*:*) _pf_e="${_pf_rest%%:*}"; _pf_rest="${_pf_rest#*:}" ;;
		*) _pf_e="$_pf_rest"; _pf_rest="" ;;
		esac
		[ "$_pf_e" = "$1" ] || _pf_new="$_pf_new:$_pf_e"
	done
	PATH="$_pf_new"
	unset _pf_new _pf_rest _pf_e
}
```

I tested this version under `sh`, `bash` and `zsh`, and it is idempotent
when sourced twice. It also removes the need for `set -f`. The old function
turned globbing back on with `set +f`, even when the caller disabled it.

## Blocker 2: Phase 4 writes with `chezmoi apply`

The README says the owner banned `chezmoi apply` after the 2026-11-09
incident. Phase 4 step 3 runs `chezmoi apply --dry-run` and then
`chezmoi apply`. Drop both. Use `chezmoi diff` for the review and
`chezmoi cat` for the content. This matches the restore procedure that
already worked.

One trap applies to this install. `~/.zshenv` is a symlink. A redirect such
as `chezmoi cat ~/.zshenv > ~/.zshenv` follows the link and truncates
`~/.shell/.zshenv`, which holds the only copy of the Jira and Bitbucket
tokens. Write to a temp file in `$HOME`, then `mv` it over the link. The
rename replaces the link and does not follow it:

```sh
stage=$(mktemp "$HOME/.zshenv.XXXXXX")
chezmoi cat "$HOME/.zshenv" > "$stage"
chmod 644 "$stage"
mv "$stage" "$HOME/.zshenv"
```

Add `--extra .shell/.zshenv` to `.shell_helper/backup_targets.sh`. The
script copies the targets that `chezmoi status` lists. The token file is
not one of them, and it is the file the install can destroy.

Install `~/.shell/bashrc.local` before `~/.bashrc`. The move of the Kiro
line and the FastPath block must happen before the managed file replaces
the live file. The Kiro line also lives in `~/.profile` and
`~/.bash_profile`, so only the FastPath block is at risk of loss.

After a by-hand write, `chezmoi status` can still show `M` in the first
column. That column compares the live file with the last state written by
chezmoi. Only an apply updates that state. Use `chezmoi diff` to prove the
target state. It compares the live file with the target state.

## Defect 3: the `cli.json` snippet breaks JSON

The design shows the extra keys as a standalone block with `"session"` and
`"diffs"` objects. Inserted into the file, that block creates two `session`
keys and two `diffs` keys. A JSON parser keeps the last one, so the extra
keys disappear or replace the base keys.

Put the condition inside each object, and keep the comma in the true
branch:

```gotemplate
  "session": {
    "thinking": "show",
    "grouping": "auto",
    "verbosity": "medium"{{ if $host.opencode_cli_extra }},
    "image_preview": false,
    "sidebar": "auto",
    "markdown": "rendered",
    "permissions": "prompt"{{ end }}
  },
  "diffs": {
    "single": true,
    "view": "unified"{{ if $host.opencode_cli_extra }},
    "wrap": "word"{{ end }}
  },
```

Render both branches and parse each result with `python3 -m json.tool`
before the install.

## Defect 4: the Homebrew block is missing

The design says the Homebrew prefix must come before `/usr/bin`. It gives
no code and no call site. Add this block before the helper call. Call the
helper last, so it keeps the first position:

```sh
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

_path_front "$HOME/.shell/helper"
```

A simulated login shell with this file puts the helper at position 1 and
`/opt/homebrew/bin` before `/usr/bin`. Both `zsh -c` and `zsh -lc` then
resolve `python3` to 3.15.2. The helper is present once after a double
source.

## Defect 5: the verification list is stale

`chezmoi status` at HEAD lists 12 targets, not "only cli.json":

```text
M .agents/rules.opencode/web-verification.md
M .bashrc
R .chezmoiscripts/start-embeddings-proxy.sh
A .config/environment.d
A .config/environment.d/10-shell-env.conf
MM .config/opencode/cli.json
M .config/opencode/opencode.jsonc
M .config/zed/settings.json
A .shell/env
A .shell/env/path.sh
M .shell/zsh/10-common-export.zsh
M .zshenv
```

The expected end state after the install is an empty `chezmoi diff`. The
`R .chezmoiscripts/start-embeddings-proxy.sh` row is pre-existing drift and
is not a diff.

## Stale or overstated text

- F4 says the Kiro line "disappears in an interactive bash". A login bash
  reads `~/.bash_profile`, which holds the line. The line disappears only
  from a non-login interactive bash that reads `~/.bashrc` alone.
- `02-design` says `include` and `includeTemplate` both resolve in
  `.chezmoitemplates`. Only `includeTemplate` does. `include` resolves from
  the source directory, so the explicit path in the design works.
- The `path.sh` header says every non-interactive bash reads the file
  through `BASH_ENV`. On this host `BASH_ENV` is unset. On macOS the file
  reaches zsh and interactive bash only. Either set `BASH_ENV` on macOS or
  narrow the comment.
- Phase 3 step 2 says the `environment.d` ignore is "gated on the OS".
  Name it: ignore `.config/environment.d` when `.chezmoi.os` is `darwin`,
  and deploy it on Linux.
- `.chezmoidata.yaml` already has `system_environment.profile`, and the
  `chezmoi` skill describes it as the machine-specific switch. No template
  reads it today. Say whether the router replaces it or reads it. Two
  parallel mechanisms invite drift.
- The repo is public, and the work hostname appears in tracked plan
  files. If the asset tag must stay private, key the table on a neutral
  label. Record the decision either way.
- The README said "four ways" and the findings list five. It now says
  five. The index said "six defects". It now says five.
- The deferred note says the host has no `zsh/zcompile` module. The module
  load fails because `zcompile` is a builtin in zsh 5.9. `zcompile` works
  and writes a `0444` file. Close the note. The mtime rule still explains
  why a newer source wins over a stale `.zwc`.
- The "Current status" section named two sandbox directories that no
  longer exist. The README now records the state at HEAD.
- The `warming.duration` check was not reproduced. The live server still
  resolves `warming: true`, and a temporary `XDG_CONFIG_HOME` did not
  change the resolved config. The schema accepts any string. Check the
  value after the install with `opencode debug config`.
- F2's exact PATH positions were not reproduced. Re-measure with the
  corrected function. The current numbers are suspect because the measured
  function duplicates entries in zsh.

## Edits by file

| File | Edit |
|---|---|
| `01-findings.md` | Correct the F2 interactive claim. Correct the F4 shell type. |
| `02-design.md` | Replace the loop. Add the Homebrew block. Fix the `include` sentence. Inline the `cli.json` keys. |
| `03-implementation.md` | Replace Phase 4 with the `chezmoi cat` install. Add the backup extras and the symlink-safe write. Fix the verification list. |
| `README.md` | Add this file to the index. Update the executive summary and the current status. |

## Not checked

- The exact PATH order on a real interactive shell after the change. The
  simulation covers the startup files, not p10k and zgenom.
- The value format for `warming.duration`. It needs the live service.
- The full Zed render with the new font families. The font files are
  present, but Zed was not restarted.
