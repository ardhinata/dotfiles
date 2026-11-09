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
that directory and because `include` and `includeTemplate` resolve there.
The file `hosts.yaml` holds the table. The file `host.yaml.tmpl` holds the
resolver.

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
	_pf_rest=""
	_pf_ifs="$IFS"
	IFS=:
	set -f
	for _pf_e in $PATH; do
		[ "$_pf_e" = "$1" ] && continue
		_pf_rest="${_pf_rest:+$_pf_rest:}$_pf_e"
	done
	set +f
	IFS="$_pf_ifs"
	PATH="$1${_pf_rest:+:$_pf_rest}"
	unset _pf_e _pf_ifs _pf_rest
}
```

The plan needs the loop. A parameter expansion cannot remove one element
from the middle of PATH. The expansion `PATH="$1:${PATH#*:$1:}"` removes
every entry before the element, not the element itself. A first draft of
this plan used that expansion, and the measured PATH lost `/usr/bin`,
`/bin`, `/usr/sbin` and `/usr/local/bin`.

The measured result with the loop: the interactive login shell puts
`/opt/homebrew/bin` at position 2, the helper at position 4 and `/usr/bin`
at position 7. The non-interactive `zsh -c` puts the helper at position 1,
`/opt/homebrew/bin` at position 3 and `/usr/bin` at position 4. Both
resolve `python3` to `/opt/homebrew/bin/python3`.

The file must stay POSIX sh. The loop above runs under `sh`, `bash` and
`zsh`. The known limit is that the loop drops an empty PATH element. An
empty element puts the current directory on PATH, and the file already
treats that as a hazard.

## The OpenCode `cli.json`

The repo file becomes `private_cli.json.tmpl`. The five keys sit behind the
router, so they reach this host only.

```gotemplate
{{- $host := fromYaml (includeTemplate "host.yaml.tmpl" .) -}}
{{- if $host.opencode_cli_extra -}}
"session": { "image_preview": false, "sidebar": "auto", "markdown": "rendered", "permissions": "prompt" },
"diffs": { "wrap": "word" },
{{- end -}}
```
