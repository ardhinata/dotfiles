---
status: fixed
severity: minor
captured: 2026-11-13
resolved: 2026-11-13
---

# Identity-specific template sections now use one common helper

## Summary

The templates no longer hold inline OS and host conditions. A common helper in
`.chezmoitemplates/section.tmpl` selects a resource file by hostname, profile,
OS, or default. The old `hosts.yaml` and `host.yaml.tmpl` are retired. The
OpenCode `cli.json` is a plain file.

The change is implemented on the Linux host and uncommitted. `chezmoi apply`
did not run.

## What changed

| Path | Change |
|---|---|
| `.chezmoitemplates/section.tmpl` | New common helper |
| `.chezmoitemplates/hosts.yaml`, `host.yaml.tmpl` | Deleted |
| `dot_zshrc.tmpl` | The prezto OS block moved to `.dot_zshrc.resources/` |
| `dot_shell/dot_zshenv.tmpl` | The Jira and Bitbucket block moved to `dot_shell/.dot_zshenv.resources/` |
| `dot_config/tmux/tmux.conf.tmpl` | Three OS conditions replaced by one `$clip` variable |
| `private_dot_gnupg/private_gpg-agent.conf.tmpl` | The OS conditions replaced by one `$pinentry` variable and a `lookPath` guard |
| `dot_config/opencode/private_cli.json` (was `.tmpl`) | Plain JSON with the work-laptop keys |
| `.agents/skills/chezmoi/SKILL.md` | New "Identity Section Includes" convention |
| `AGENTS.md` | Pointer updated |

The related documents were updated: `docs/how-to/prezto-modules-per-os.md`,
`.agents/docs/macos-host-handoff.md`, `docs/reports/README.md`, the superseded
note in `docs/plans/2026-11-09-macos-host-router-and-upstream-apply/README.md`,
the note in `docs/plans/2026-11-03-macos-pinentry-mac.md`, and the later-change
note in `docs/reports/2026-11-03-macos-host-portability.md`.

## The mechanism

The helper tries four names in order and uses the first that exists:

1. `<section>.h_<hostname>`
2. `<section>.p_<profile>`
3. `<section>.os_<os>`
4. `<section>._default`

The hostname and the profile are lowercased and sanitized to `[a-z0-9-]`.

The resource directory is a sibling of the template:

```
<dir of file>/.<base of file without .tmpl>.resources/
```

A caller passes the source path and the section name:

```gotemplate
{{ template "section.tmpl" (dict "root" . "file" "dot_zshrc.tmpl" "section" "prezto-platform") }}
```

The helper tests each candidate with `stat` on an absolute path. It executes the
selected file with `includeTemplate`, logs the chosen candidate with `debugf`,
and warns when no candidate and no `_default` exist. A missing `include` aborts
the render, so the `stat` guard is required.

## Verification

The five targets were rendered before and after the change.

| Target | Result |
|---|---|
| `~/.zshrc` | Byte-identical |
| `~/.shell/.zshenv` on Linux | Byte-identical |
| `~/.config/tmux/tmux.conf` | Byte-identical |
| `~/.gnupg/gpg-agent.conf` | Byte-identical |
| `~/.config/opencode/cli.json` | Gains the work-laptop keys on purpose |

Commands:

```sh
chezmoi cat ~/.zshrc
chezmoi cat ~/.shell/.zshenv
chezmoi cat ~/.config/tmux/tmux.conf
chezmoi cat ~/.gnupg/gpg-agent.conf
chezmoi cat ~/.config/opencode/cli.json
chezmoi -v cat ~/.zshrc
chezmoi diff
chezmoi status
chezmoi managed
```

Results:

- `zsh -n` on the rendered `.zshrc` passed.
- `bash -n` on the rendered `.zshenv` passed.
- `python3 -m json.tool` on the plain `cli.json` passed.
- `chezmoi diff` shows only the `cli.json` keys.
- `chezmoi status` shows `M .config/opencode/cli.json` and the pre-existing
  `start-embeddings-proxy.sh` rename.
- `chezmoi managed` lists no router file and no resource file.
- The host, profile, OS, default, debug, and missing-default paths were tested.

## Cross-system handoff

The work laptop uses `shellx-secrets.h_ikm202300278` for the `.zshenv` block.
The file name uses the lowercased short hostname. A hostname change needs a
renamed resource.

The Linux host uses the empty `_default` and gets no Jira or Bitbucket block.

`cli.json` is plain and applies the work-laptop keys on every host. This is
intended.

The changes are uncommitted on the Linux host. The work laptop cannot see them
until the user commits and pushes. Do not run `chezmoi apply` in the source
repo. On the macOS host, follow `.agents/docs/macos-host-handoff.md`.

The `p_` tier uses `system_environment.profile`. Set it to a group name before
the first `p_` resource. It is the hostname on the Linux host today.

## Risks and limits

- The Darwin branch of `gpg-agent.conf` and the `os_darwin` zshrc resource were
  not rendered on the Linux host. Their content was copied from the old
  template. Render them on the Mac.
- The bare hostname stays in the tree. The git history already holds it. A
  history rewrite is a separate decision.
- A block resource ends without a trailing newline. The template supplies the
  final newline. A trailing newline adds a blank line, not a break.
- Every section needs a `_default`. A missing default warns.
- The stale profile and slug comment at
  `dot_shell/helper/private_shellx_impl.py.tmpl:219-223` still needs a separate
  code change. It says the profile is part of the static password. The code
  derives the slug from the master key.

## Related

- [Plan](../plans/2026-11-13-chezmoi-identity-section-includes.md)
- [Agent note](../../.agents/docs/identity-section-includes.md)
- [Chezmoi skill](../../.agents/skills/chezmoi/SKILL.md)
- [Retired router plan](../plans/2026-11-09-macos-host-router-and-upstream-apply/)
