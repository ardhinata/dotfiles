# Identity section includes

A template that needs machine-specific content calls the common helper
`.chezmoitemplates/section.tmpl`. Do not add a new inline `if eq .chezmoi.os`
block.

## Call shape

```gotemplate
{{ template "section.tmpl" (dict "root" . "file" "dot_zshrc.tmpl" "section" "prezto-platform") }}
```

`file` is the source path relative to the repo root, including `.tmpl`. The
helper derives the resource directory from it.

## Resolution order

1. `<section>.h_<hostname>`
2. `<section>.p_<profile>`
3. `<section>.os_<os>`
4. `<section>._default`

The hostname and the profile are lowercased and sanitized to `[a-z0-9-]`.

## Resource layout

```
<dir of file>/.<base of file without .tmpl>.resources/
```

Current resources:

- `.dot_zshrc.resources/prezto-platform.os_darwin`
- `.dot_zshrc.resources/prezto-platform.os_linux`
- `.dot_zshrc.resources/prezto-platform._default` (empty)
- `dot_shell/.dot_zshenv.resources/shellx-secrets.h_ikm202300278`
- `dot_shell/.dot_zshenv.resources/shellx-secrets._default` (empty)

The OpenCode `cli.json` has no template and no resource. It is plain JSON with
the work-laptop keys on every host.

## Rules

- Give every section a `_default`, even an empty one.
- A block resource starts with the blank lines it needs and ends without a
  trailing newline. The template supplies the final newline.
- A fragment inside a line uses `trim (includeTemplate ...)`.
- The helper logs the chosen candidate with `debugf`. Run
  `chezmoi -v cat <target>`.
- A resource is a Go template. Escape a literal `{{`.
- `.chezmoiignore` keeps its inline OS conditions. `lookPath` conditions stay
  inline too. The helper selects on identity only.

## Current state, 2026-11-13

The Linux host (`horiuchi-aika`) uses `prezto-platform.os_linux` and the empty
`shellx-secrets._default`.

The work laptop uses `shellx-secrets.h_ikm202300278`. If its hostname changes,
rename the resource.

The changes are uncommitted on the Linux host. Commit and push before the macOS
host pulls.

`chezmoi apply` did not run. On the Linux host, `chezmoi diff` shows only the
`cli.json` keys.

## Verify without apply

```sh
chezmoi cat ~/.zshrc
chezmoi cat ~/.shell/.zshenv
chezmoi -v cat ~/.zshrc
chezmoi diff
chezmoi status
chezmoi managed | grep -E 'hosts.yaml|host.yaml|\.resources'
```

The last command must print nothing.

## Retired

`.chezmoitemplates/hosts.yaml` and `host.yaml.tmpl` are gone. A checkout that
still references them fails. The old hostname router is in
`docs/plans/2026-11-09-macos-host-router-and-upstream-apply/` as history.

## See also

- [Report](../../docs/reports/2026-11-13-identity-section-includes.md)
- [Plan](../../docs/plans/2026-11-13-chezmoi-identity-section-includes.md)
- [Chezmoi skill](../skills/chezmoi/SKILL.md)
