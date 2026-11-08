# macOS apply target state

The 53 targets a `chezmoi apply` changes on the macOS host, and the
decisions each one needs. Companions:
[`macos-apply-blockers.md`](macos-apply-blockers.md) holds the blockers,
and [`macos-apply-caveats.md`](macos-apply-caveats.md) holds the changes
that do not block.

Verified on 2026-11-03 with `chezmoi apply --dry-run --force --verbose`
after `chezmoi init` ran on this host.

## No SSH key reaches this host

No `~/.ssh/config.d/*.conf` and no `~/.ssh/keys/*` file appears in the
diff. The encrypted SSH material stays off this host. `chezmoi ignored`
lists all 9 `config.d` files and all 15 `keys` files.

## The apply must not run yet

Six blockers stand between this host and a clean apply. They are in
[`macos-apply-blockers.md`](macos-apply-blockers.md). Blocker 1 is
resolved: the live launchd agent was removed, so the repo agent is the
only one. The rest still stand:

- **`chezmoi init` must run first.** The live config has no
  `system_environment.nonce`, so every chezmoi command that renders the
  target state fails and `chezmoi status` returns nothing. `chezmoi init`
  prompts for the profile and generates the nonce.
- **`~/.zshrc` and `~/.zprofile` change shape.** Both are symlinks into
  `~/.shell/` today. The apply replaces them with plain files, which
  orphans the live `~/.shell/useropts/` layer. The gap list and the backup
  location are in blocker 2.
- **The shellx store does not exist here.** The apply produces a shell
  that reads the OpenRouter key from a store that is not on this host.

## Back up before applying

```bash
CHEZMOI_CONFIG=<config> .shell_helper/backup_targets.sh \
  ~/.local/state/chezmoi-backup-<date> \
  --extra .ssh/config.d/github.single.conf \
  --extra .ssh/config.d/bitbucket.group.conf \
  --extra .ssh/config.d/home.group.conf \
  --extra .ssh/config.d/local-defaults.general.conf
```

The script copies the 18 live files and records the 5 directory modes. The
`--extra` paths are the SSH fragments, which chezmoi does not manage but
which the apply disturbs.

Restore:

```bash
.shell_helper/backup_targets.sh --restore ~/.local/state/chezmoi-backup-<date>
```

The restore does not delete files the apply created. Remove those with
`chezmoi destroy <target>`.

## Deliberate, low risk

| Target | Change |
|---|---|
| `~/.config/opencode/agents/*.md` | 4 new files. Model-pinned subagent variants for the OpenCode Go subscription. |
| `~/.config/opencode/skills/subagent-routing/SKILL.md` | New file. Rolls a random model for each subagent call. |
| `~/.config/opencode/opencode.jsonc` | Drops the ensemble plugin. Adds the `context7` MCP server, disabled by default. Deny rules for `tavily-defaults` and `spec-kit`. |
| `~/.config/opencode/cli.json` | Adds `debug.turn_tokens`. |
| `~/.agents/rules.opencode/ensemble-teams.md` | Deleted. The ensemble plugin is gone. |
| `~/.agents/skills/zsh-stack/SKILL.md` | Text update. |
| `~/.agents/skills/asd-ste100/scripts/ste_check.py` | Mode 0755 to 0644. The script is called with `python3`, so the exec bit is not needed. |
| `~/.gnupg/gpg-agent.conf` | Gains `enable-ssh-support` and the ssh cache TTLs. The live file has no `enable-ssh-support`, so the agent does not serve ssh today. |

## Needs a decision

| Target | Change | Why it matters |
|---|---|---|
| `~/.ssh` | Directory mode 0700 to 0755. | The live directory is 0700. The repo has no `private_` prefix on `dot_ssh`. |
| `~/.gitconfig` | Name, email, and signing key change to the `Ardhinata Juari` identity. `commit.gpgSign` and `core.editor` disappear. | The live file uses the `Muhamad Ardhinata J.` identity with `gpgSign = yes`. The repo version is the personal identity. Pick one before applying. |
| `~/.p10k.zsh` | Replaced by the 2026-05-24 wizard output. The live file is the 2026-06-18 output. | The live file is newer. Applying moves the prompt backwards. |
| `~/.config/tmux/tmux.conf` | The live file was hand-edited for macOS. The repo version adds `extkeys` back to `terminal-features` and restores the shared Wayland wording. The only other differences are comment lines. | The repo version renders `pbcopy` on darwin, so the clipboard bridge stays. It is still a downgrade from the live file. |
| `~/.gnupg/gpg.conf` | New file with `default-key 9909A0802A11B93F`. | The live host has no `gpg.conf`. The key ID in the new file matches neither signing key in the local keyring. |
| `~/.gnupg/common.conf` | Mode 0640 to 0644. | The `private_` prefix is on the directory, not the file. |
| `~/.config/zed/settings.json` | Drops `allow_rewrap`, `use_system_prompts`, `use_system_path_prompts`. Changes the buffer font to RobotoMono. | The live file is a newer local edit. |
| `~/.config/alacritty/alacritty.toml` | Font family changes to "Terminess Nerd Font", and the bold/italic/bold-italic variants are commented out. | The comment explains a KDE compositor tearing bug. The fix is Linux-specific. |
| `~/.config/cortexkit/aft.jsonc` | New embedding salt and a 384-dimension width. | Changes the AFT index fingerprint. The 681 MB index in `~/.local/share/cortexkit` rebuilds. |
| `~/.config/cortexkit/magic-context.jsonc` | Model changes to `opencode-go/deepseek-v4.1-flash`. Injection budget 6000 to 6144. | Needs the OpenCode Go subscription. |
| `~/.cc-safety-net/policy.json` | Removes the `rm.recursive-force-outside-cwd` and the secret-extension overrides. | Tightens the safety net. The live file has those protections off. |

## Converges to the repo layout

| Target | Change |
|---|---|
| `~/.zshrc` | The live file is a symlink to `~/.shell/.zshrc`. The repo deploys a plain file. The live file also has a Kiro CLI preamble and a `useropts/` layout that the repo does not have. |
| `~/.zprofile` | Same symlink change. |
| `~/.shell/zsh/*.zsh` | New directory. The repo layout puts the zsh helpers in `~/.shell/zsh/`. The live host uses `~/.shell/useropts/`. |
| `~/.shell/helper/shellx*` | The shellx helper and its two modules. The live host has only `embedding_dimensions_proxy.py`. |
| `~/.local/share/shellx/master.key` | New file, mode 0600. Derived from the nonce. |
| `~/.config/cortexkit` | Directory mode 0700 to 0755. |
| `~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` | New file. The live host runs a different label. See the caveats note. |

## SSH config

The repo `dot_ssh/config` holds three `Include` lines and a `Host *`
block. The live `~/.ssh/config` held 37 lines of host entries:

```text
Host bitbucket.org
Host home.mindbreak.info
Host github.com
Host horiuchi-aika.home.mindbreak.info
Host personal-bitbucket.mindbreak.info
```

Each named a local `IdentityFile` under `~/.ssh/`. Applying the repo
version over the live file removed all of them. The `Include` lines that
replace them point at files that stay encrypted and therefore stay off
this host. So `ssh` to those hosts stopped working.

Resolved on 2026-11-03. The host entries moved into `~/.ssh/config.d/`
as classified fragments, and the live `~/.ssh/config` is now the repo
file unchanged:

| File | Class | Hosts |
|---|---|---|
| `github.single.conf` | single | `github.com` |
| `bitbucket.group.conf` | group | `bitbucket.org`, `personal-bitbucket.mindbreak.info` |
| `home.group.conf` | group | `home.mindbreak.info`, `horiuchi-aika.home.mindbreak.info` |
| `local-defaults.general.conf` | general | The default identities for every host. |

`ssh -G` output is unchanged for every host except `identitiesonly`,
which the repo `Host *` block sets to `yes`. The agent holds no
identities on this host, so that setting is inert here.

The fragments live only in `~/.ssh/config.d/`. They are not in the
source tree, so chezmoi does not manage them and an apply does not
remove them. They name identity files that exist only on this host.

## Shell layout warning

The repo `dot_zshrc.tmpl` sources `~/.shell/zsh/00-before-zgenom.zsh` and the
other files in that directory. It does not source `~/.shell/useropts/`.
The live host sources `useropts/` from `~/.shell/.zshrc`. Applying
replaces the live `~/.zshrc` with the repo version, so the `useropts/`
files stop being sourced. They stay on disk.

Move their content into the repo layout or keep the live `~/.zshrc`
before applying. The live `useropts/` set holds `00-brew-fix.zsh`,
`00-zgenom.zsh`, `01-openblas.zsh`, `02-bun.zsh`, `02-opencode.zsh`,
`03-compinit.zsh`, and `99-sdkman.zsh`.

## See also

- [`macos-apply-blockers.md`](macos-apply-blockers.md) — the blockers and the caveats
- [`macos-host-handoff.md`](macos-host-handoff.md) — the portable source state
