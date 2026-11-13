---
status: draft
goal: Move identity-specific sections out of chezmoi templates into resource files and retire the host map
owner: ardhinata
last-updated: 2026-11-13
---

# Split identity-specific sections out of the chezmoi templates

## Goal

A template must show only its shared content. Content that depends on the
machine must live in a resource file next to the template. The file name
selects the machine. The tree must have one identity mechanism, not two.

## Scope

- In: a section resolver, the resource naming convention, the conversion of the
  current inline OS conditions, and the retirement of `hosts.yaml`.
- Out: `.chezmoiignore`, the `lookPath` conditions, the shellx store format, and
  the git history.

## Research findings

### Measured template behavior

All checks ran on chezmoi v2.74.1.

| Check | Result |
|---|---|
| `include` on a missing file | Aborts the template with exit 1 |
| `include` on an absolute path | Works |
| `includeTemplate` on an absolute path | Works and renders `{{ ... }}` with the data |
| `stat` on a relative path | Resolves from `$HOME`, not the source directory |
| `stat` on a missing file | Returns false, no error |
| A dot-prefixed source directory | Does not appear in `chezmoi managed` |
| `break` inside `range` | Works |
| `merge a b` | `a` wins on a key conflict |
| `sha256sum`, `trunc`, `lower`, `regexReplaceAll` | Available |

Two consequences follow.

1. A section lookup must test each candidate with `stat` on an absolute path.
   A blind `include` aborts the whole apply.
2. A resource can use `.chezmoi` and the data, because the resolver uses
   `includeTemplate`. A raw `include` emits the template text unchanged.

### Current inline conditions

| File | Lines | Condition | Shape | Plan |
|---|---|---|---|---|
| `dot_zshrc.tmpl` | 70–94 | `.chezmoi.os` | 25-line block | Section |
| `dot_config/tmux/tmux.conf.tmpl` | 179, 214, 215 | `.chezmoi.os` | One word, three times | One variable |
| `private_dot_gnupg/private_gpg-agent.conf.tmpl` | 3–17 | `.chezmoi.os` and `lookPath` | Comment and line | One variable and a guard |
| `dot_config/opencode/private_cli.json.tmpl` | 1, 8, 16 | Host flag | JSON keys | Two fragment sections |
| `dot_shell/dot_zshenv.tmpl` | 7–10 | Host label | Secret block | One section |
| `.chezmoiignore` | 50–74 | `.chezmoi.os` | Ignore patterns | Keep inline |
| `dot_agents/exact_rules/runtime-tools.md.tmpl` | 21–43 | `lookPath` | Blocks | Already includes |

The tree has three template files with inline OS conditions, not seven. Two
files read the host map. The problem is real, but it is small.

### The host map has two consumers

| Consumer | Use | Replacement |
|---|---|---|
| `dot_shell/dot_zshenv.tmpl` | `label == "work-laptop"` gates the Jira and Bitbucket block | `shellx-secrets` section |
| `dot_config/opencode/private_cli.json.tmpl` | `opencode_cli_extra` adds five keys in two objects | `session-extra` and `diffs-extra` sections |

No other file reads `hosts.yaml` or `host.yaml.tmpl`. The retirement is small.

### One identity mechanism

The router maps a hostname to a label and a flag. The section resolver maps a
hostname, a profile, and an OS to a file. Both answer the same question. Keep
the resolver and delete the router.

The router also warns on an unknown host. The section resolver gives the same
safety with an empty `_default`: an unknown host loses the override, and it
does not receive another host's content.

### Host identifier

Decision: use the bare hostname. The work hostname is already in 7 tracked
files, on 8 lines, and in git history. A hash on new files does not remove
those copies and is reversible. The plan does not add a hash and does not
rewrite history.

The resolver lowercases the hostname, so a case difference cannot split the
lookup.

## Refined approach

### Resolution order

The resolver tests four candidates in this order:

1. `h_<hostname>`: the individual machine.
2. `p_<profile>`: the machine group.
3. `os_<os>`: the platform.
4. `_default`: the fallback.

The first file that exists wins. A section should have a `_default`, so a new
machine gets content instead of a warning. The resolver warns when no candidate
matches.

The OS tier is the addition to the rough plan. Most current conditions are OS
conditions, not host conditions. Without the OS tier, each macOS host needs a
copy of the same block.

### Directory and file names

The resource directory is a sibling of the template. Its name is a dot, the
base name of the source file without `.tmpl`, and `.resources`:

| Template | Resource directory |
|---|---|
| `dot_zshrc.tmpl` | `.dot_zshrc.resources/` |
| `dot_shell/dot_zshenv.tmpl` | `dot_shell/.dot_zshenv.resources/` |
| `dot_config/opencode/private_cli.json.tmpl` | `dot_config/opencode/.private_cli.json.resources/` |

chezmoi ignores a dot directory, so it never reaches `$HOME` and needs no
`.chezmoiignore` entry.

A resource file is `<section>.<identifier>`:

```
.dot_zshrc.resources/
  prezto-platform.h_<hostname>
  prezto-platform.p_linux-home
  prezto-platform.os_darwin
  prezto-platform._default
```

The rough plan repeated the template name inside the file name. The directory
already carries that name, so the repeat is redundant and can drift.

A section name is better than a number. A name survives a reorder. A number
does not.

### The common helper

`.chezmoitemplates/section.tmpl`:

```gotemplate
{{- $r := .root -}}
{{- $base := trimSuffix ".tmpl" (base .file) -}}
{{- $dir := joinPath $r.chezmoi.sourceDir (dir .file) (printf ".%s.resources" $base) -}}
{{- $profile := regexReplaceAll "[^a-z0-9-]" (lower (dig "system_environment" "profile" "" $r)) "-" -}}
{{- $host := printf "h_%s" (regexReplaceAll "[^a-z0-9-]" (lower $r.chezmoi.hostname) "-") -}}
{{- $cands := list
      (printf "%s.%s" .section $host)
      (printf "%s.p_%s" .section $profile)
      (printf "%s.os_%s" .section $r.chezmoi.os)
      (printf "%s._default" .section) -}}
{{- $found := false -}}
{{- range $c := $cands -}}
{{-   $p := joinPath $dir $c -}}
{{-   if and (not $found) (stat $p) -}}
{{-     $found = true -}}
{{-     debugf "section %q of %q: using %s" $.section $.file $c -}}
{{-     includeTemplate $p $r -}}
{{-   end -}}
{{- end -}}
{{- if not $found -}}
{{-   warnf "section %q of %q: no resource and no _default" $.section $.file -}}
{{- end -}}
```

A caller:

```gotemplate
{{ template "section.tmpl" (dict "root" . "file" "dot_zshrc.tmpl" "section" "prezto-platform") }}
```

The helper is the common mechanism. A template repeats only the call. It does
not repeat the lookup, the `stat` guard, the fallback, or the `debugf` line.

A prototype of the helper passed on a throwaway source tree. It selected the
OS tier, then the host tier, and it warned on a missing section.

### Retire the host map

The `.zshenv` block moves to
`dot_shell/.dot_zshenv.resources/shellx-secrets.h_<hostname>`. The `_default`
file is empty. The template drops the router line and the `if`, and it calls
the section.

The OpenCode flags become two fragment sections. The resource owns the leading
comma, so the output is valid JSON in both cases:

```json
,
    "image_preview": false,
    "sidebar": "auto",
    "markdown": "rendered",
    "permissions": "prompt"
```

```json
,
    "wrap": "word"
```

The template keeps the shared key and calls the section after it:

```gotemplate
"verbosity": "medium"{{ template "section.tmpl" (dict "root" . "file" "dot_config/opencode/private_cli.json.tmpl" "section" "session-extra") }}
```

Then delete `.chezmoitemplates/hosts.yaml` and
`.chezmoitemplates/host.yaml.tmpl`.

### What stays inline

| Case | Why |
|---|---|
| `.chezmoiignore` | It holds ignore patterns, not content. A directory next to it starts with `.chezmoi`, which chezmoi does not ignore |
| `lookPath` conditions | Tool presence is machine state. The resolver selects on identity only |

### Section, variable, or data

| Shape | Use |
|---|---|
| A multi-line block | A section |
| A word inside a line | A variable |
| A flag for a structural format | An empty or fragment section |

A section resource keeps its trailing newline. A one-word resource therefore
breaks an inline command. This is why the tmux clipboard word and the gpg
pinentry line use a variable, not a section.

## Implementation steps

1. Add the common helper `.chezmoitemplates/section.tmpl`. Every template
   calls it with the `template` action.
2. Convert the prezto block in `dot_zshrc.tmpl` to a section. Add the two OS
   resources and an empty `_default`.
3. Move the Jira and Bitbucket block from `dot_shell/dot_zshenv.tmpl` to the
   `shellx-secrets` section.
4. Move the OpenCode extras to the `session-extra` and `diffs-extra` sections.
5. Delete `.chezmoitemplates/hosts.yaml` and
   `.chezmoitemplates/host.yaml.tmpl`.
6. Replace the three tmux conditions with one `$clip` variable.
7. Replace the gpg conditions with one `$pinentry` variable and a `lookPath`
   guard.
8. Record the convention in `.agents/skills/chezmoi/SKILL.md`. Include the
   resolution order, the section-name rule, and the `{{` escape rule.
9. Update the `AGENTS.md` pointer that calls the router current.
10. Test each tier and run `chezmoi diff`.

## Verification

| Check | Command |
|---|---|
| The shell template renders | `chezmoi cat ~/.zshrc` |
| The secrets render | `chezmoi cat ~/.shell/.zshenv` |
| Both JSON variants are valid | `chezmoi cat ~/.config/opencode/cli.json \| python3 -m json.tool`, with and without the host resource |
| The chosen section is visible | `chezmoi -v cat ~/.zshrc 2>&1 \| grep 'using'` |
| The router is gone | `chezmoi managed \| grep -c 'hosts.yaml\|host.yaml'` returns 0 |
| The tree is clean | `chezmoi diff` and `chezmoi status` |
| The host tier wins | Create `prezto-platform.h_<hostname>`, render, remove |
| The profile tier works | Set a test profile in the untracked config, render |
| The OS tier works | Render on Linux and on macOS |
| The missing default warns | Call a section with no resource and no `_default` |

## Risks and mitigations

- Risk: the JSON fragment has a bad comma, so `cli.json` is invalid. Mitigation:
  render both variants and parse each with `python3 -m json.tool`.
- Risk: a renamed host loses the override. Mitigation: the empty `_default`
  gives the safe result. It does not grant another host's secrets.
- Risk: a resource has a stray `{{`, so the render aborts. Mitigation: render
  every target after the change.
- Risk: `stat` is not hermetic. Mitigation: it reads only the source tree, which
  does not change during a render.
- Risk: the bare hostname adds copies to the tree. Mitigation: the tree already
  carries the name, and the change removes `hosts.yaml`. No new secret is
  exposed.

## Open questions

None. The decisions below are final for this plan.

## Decisions

- 2026-11-13: Use the bare hostname. Hashing is not worth it while the history
  already exposes the name.
- 2026-11-13: Retire `hosts.yaml` and `host.yaml.tmpl`. The resolver replaces
  both consumers.
- 2026-11-13: Add the OS tier between the profile and the default.
- 2026-11-13: Use the host tier for the two migrated consumers.
- 2026-11-13: Log the chosen candidate with `debugf`. Keep `warnf` only when no
  candidate and no `_default` exist.
- 2026-11-13: Use section names, not numbers.
- 2026-11-13: Call the common helper with the `template` action. Use
  `includeTemplate` inside it for the selected resource.
  Document the `{{` escape rule.
- 2026-11-13: Use section files for blocks and variables for words.

## Deferred notes

- The git history still holds the work hostname. A history rewrite is possible
  but destructive. It is a separate decision.
- The comment at `dot_shell/helper/private_shellx_impl.py.tmpl:219-223` says the
  profile is part of the static password. The code derives the slug from the
  master key. Fix the comment in a separate change.
- `dot_agents/exact_rules/.template-resources/` uses a shared directory and
  tool-presence keys. Leave it. It does not select on identity.

## Current status

Research is complete. All design questions are closed. The resolver passed a
prototype on a throwaway source tree. No source file changed yet.
