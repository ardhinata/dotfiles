# Design

Three layers, from the most specific to the most general. This design fixes
the defects in [01-findings.md](01-findings.md). Part of the plan to correct
the dotfiles for the macOS work laptop. See [README.md](README.md) for the
index.

## Layer 1: presence-based dispatch

A repo file sources a host-local file when that file exists. The repo file
is the same on every host, and the content differs because the host-local
file differs.

This layer carries the secret file and the host-local shell lines. The repo
never holds a secret, and the router does not need to know the hostname.

## Layer 2: the hostname router

A table maps a hostname to a profile. The resolver returns the profile for
the current host. Use the router where the repo must render the content
itself, because JSON has no include mechanism.

The router uses the hostname and not the OS. The differences that remain
after layer 1 are per-machine. The Kiro CLI runs on this work laptop only.
The OpenCode `cli.json` keys are a personal preference. The OS cannot tell
these apart.

The router lives in `.chezmoitemplates/`, because chezmoi does not deploy
that directory. `includeTemplate` searches `.chezmoitemplates` first, so
the resolver is found by its plain name. `include` does not search it: it
resolves a path relative to the source directory, so the table is read with
the explicit path `.chezmoitemplates/hosts.yaml`.

```gotemplate
{{- $hosts := fromYaml (include ".chezmoitemplates/hosts.yaml") -}}
{{- $profile := get $hosts .chezmoi.hostname -}}
{{- if not $profile -}}
{{-   warnf "unknown host %q: using the default profile" .chezmoi.hostname -}}
{{-   $profile = get $hosts "_default" -}}
{{- end -}}
{{ toYaml $profile }}
```

A consumer reads the profile with one line:

```gotemplate
{{- $host := fromYaml (includeTemplate "host.yaml.tmpl" .) -}}
```

An unknown hostname falls back to the `_default` profile and prints a
warning. The warning is deliberate. A renamed laptop must not silently
receive another host's configuration.

The resolver, the table and the fallback were tested in a throwaway source
tree. `chezmoi --source <tmp> managed` listed only the probe file, so the
router files are not deployed.

The router and `system_environment.profile` do different jobs. The profile
selects the section of the shellx secret store. The router selects the
content the repo renders. The router does not replace the profile.

## Layer 3: the OS axis

`{{ if eq .chezmoi.os "darwin" }}` covers the platform facts. The repo
already uses this form in `.chezmoiignore` and `dot_zshrc.tmpl`.

## The dispatchers

The `~/.zshenv` target becomes a dispatcher. The token file stays at
`~/.shell/.zshenv`, and the file stays unmanaged. The `~/.bashrc` target
gains a dispatcher for `~/.shell/bashrc.local`, and the Kiro CLI line and
the FastPath block move to that file on this host.

```sh
[ -r "$HOME/.shell/env/path.sh" ] && . "$HOME/.shell/env/path.sh"
[ -r "$HOME/.shell/.zshenv" ] && . "$HOME/.shell/.zshenv"
[ -r "$HOME/.shell/bashrc.local" ] && . "$HOME/.shell/bashrc.local"
```

Both dispatchers are compile safe. `~/.zshenv.zwc` holds compiled bytecode
that still sources the token file at run time.

## The PATH fix

The `path.sh` file needs two changes for macOS. The Homebrew prefix must
come before `/usr/bin`, so that `/usr/bin/env python3` finds Python 3.15.
An entry that the file already placed must move to the front, because
`path_helper` runs after `~/.zshenv` and demotes it.

The `dot_zprofile` target must source `path.sh` a second time, because
`/etc/zprofile` runs before `~/.zprofile`.

```sh
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
```

The plan needs the loop. A parameter expansion cannot remove one element
from the middle of PATH. The expansion `PATH="$1:${PATH#*:$1:}"` removes
every entry before the element, not the element itself. A first draft of
this plan used that expansion, and the measured PATH lost `/usr/bin`,
`/bin`, `/usr/sbin` and `/usr/local/bin`.

The loop peels the first element off the rest, so it needs no word
splitting. A loop over `$PATH` does need word splitting, and zsh does not
split an unquoted expansion by default: it ran once with the whole PATH in
the variable, duplicated the entry, and left the old copy in the middle.
The peel version is correct in sh, bash and zsh, and it is idempotent when
the file is sourced twice.

The Homebrew block runs before the helper call, so the helper keeps the
first position:

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

The measured result with the corrected file: the non-interactive shell puts
the helper at position 1, `/opt/homebrew/bin` at position 2 and `/usr/bin`
at position 5. The interactive shell lists the fnm directory, the Homebrew
prefix and the cargo directory before the helper, because the interactive
startup prepends them after this file has run. The helper stays ahead of
`/usr/bin` and of `~/.local/bin`, which is what the file needs. Every one
of the four shell types resolves `python3` to `/opt/homebrew/bin/python3`.

The file must stay POSIX sh. The known limit is that the loop drops an
empty PATH element. An empty element puts the current directory on PATH,
and the file already treats that as a hazard.

## The OpenCode `cli.json`

The repo file becomes `private_cli.json.tmpl`. The five keys sit behind the
router, so they reach this host only. The condition goes inside each
object: a second `session` object would replace the first one, and the
extra keys would be lost.

```gotemplate
{{- $host := fromYaml (includeTemplate "host.yaml.tmpl" .) -}}
{
  "$schema": "https://opencode.ai/v2/cli.json",
  "animations": true,
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
  }
}
```

Both branches are rendered and parsed with `python3 -m json.tool` before the
install.
