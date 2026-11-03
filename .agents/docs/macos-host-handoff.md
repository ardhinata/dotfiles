# macOS host handoff

Read this file when you work on the macOS host of this dotfiles repo. It
names the state of the source tree, the files that the macOS host receives,
and the parts that still assume Linux. The report for human readers lives
at `docs/reports/2026-11-03-macos-host-portability.md`.

**For the current apply result on this host, read
[`macos-apply-blockers.md`](macos-apply-blockers.md),
[`macos-apply-target-state.md`](macos-apply-target-state.md),
[`macos-apply-caveats.md`](macos-apply-caveats.md) and
[`macos-apply-fixed.md`](macos-apply-fixed.md).** The first holds the
verified blockers. The second holds the 53 changed targets and the
decisions each one needs. The third holds the changes that do not block.
The fourth holds the defects the apply exposed, with the fix for each
one. This note describes the source state and the older open items.

## State of the source tree

Commit `f855bab` made the source state portable. It landed on `main` on
2026-11-03. The change is in the repo, but no macOS host ran
`chezmoi apply` with it.

## What the macOS host receives

- `~/.zshrc`, `~/.zprofile`, `~/.p10k.zsh`, `~/.gitconfig`
- `~/.gnupg/` with `gpg-agent.conf`, `gpg.conf`, and `common.conf`
- `~/.shell/` with the shellx helper, the helper scripts, and the zsh files
- `~/.config/` with the settings for alacritty, tmux, zed, cortexkit, and opencode
- `~/.agents/` with the rules and the skills
- `~/.local/share/shellx/master.key`, mode 0600
- `~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist`

## What the macOS host does not receive

- `~/.config/systemd/user/embedding-dimensions-proxy.service`
- `~/.shell/helper/pinentry-switch`
- `~/.shell/helper/pinentry-wrapper`
- `~/.shell/zsh/completions/_pinentry-switch`

On this host, the host also does not receive the encrypted SSH files:
the 9 `~/.ssh/config.d/*.conf` files and the 15 `~/.ssh/keys/*` files.
They stay encrypted, and the host has no age identity. See
[`macos-apply-blockers.md`](macos-apply-blockers.md).

chezmoi does not delete a file that it no longer manages. A copy of
`~/.shell/helper/runpriv` or `~/.shell/helper/encrypt_store.sh` stays on
disk after an apply. Remove it by hand on both hosts.

## Steps to verify the macOS host

Take a backup first. The apply changes 53 targets on this host, and it
replaces the live shell files, the git identity, and the prompt config.

```sh
CHEZMOI_CONFIG=<config> .shell_helper/backup_targets.sh \
  ~/.local/state/chezmoi-backup-$(date +%Y%m%d) \
  --extra .ssh/config.d/github.single.conf \
  --extra .ssh/config.d/bitbucket.group.conf \
  --extra .ssh/config.d/home.group.conf \
  --extra .ssh/config.d/local-defaults.general.conf
```

Then run these on the macOS host after `chezmoi apply`.

```sh
chezmoi source-path
chezmoi ignored
chezmoi cat ~/.config/tmux/tmux.conf | grep copy-pipe
chezmoi cat ~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist
launchctl print "gui/$(id -u)/com.user.embedding-dimensions-proxy"
```

The expected result of each command:

| Command | Expected result |
|---|---|
| `chezmoi ignored` | lists `.config/systemd` and the three pinentry paths. It does not list the launchd plist. |
| `chezmoi cat ~/.config/tmux/tmux.conf` | shows `copy-pipe-and-cancel "pbcopy"` |
| `chezmoi cat ~/.gitconfig` | shows `gitdir:/Users/<name>/Work/` |
| `chezmoi cat ~/.gnupg/gpg-agent.conf` | shows no `pinentry-program` line |
| `launchctl print` | shows the agent with a state and a process id |

## Open items to patch

Item 1 is **wrong for this host** and items 6 and 8 are **stale**. Both
notes are corrected below. The rest still stand.

1. **The age identity.** `.encryption_keys/personal_pq.secret.key` is not
   in git. Put it on the macOS host before the first apply, or the apply
   fails on every encrypted file.

   **Corrected on 2026-11-03.** Do **not** put the identity on this work
   laptop. The encrypted files are the personal machine's SSH keys. The
   host must stay separate. The `check_decrypt.sh` mechanism skips
   encrypted files the host cannot decrypt, so the apply succeeds with no
   identity. See
   [`macos-apply-blockers.md`](macos-apply-blockers.md).
2. **The pinentry sources.** `executable_pinentry-switch` and
   `executable_pinentry-wrapper` name `/usr/bin/pinentry-*` and use `ldd`.
   Homebrew GnuPG installs the binaries in `/opt/homebrew/bin`, and macOS
   has no `ldd`. Patch both files, then remove the three ignore lines
   from `.chezmoiignore`.
3. **`use-keyboxd`.** `private_dot_gnupg/common.conf` sets it. Homebrew
   GnuPG 2.4 supports it, but the keyboxd daemon must run. Remove the
   line if `gpg` reports a keyboxd error.

   **Verified on 2026-11-03.** The host runs GnuPG 2.5.24 with a
   `keyboxd` socket in `~/.gnupg/`. `gpg --list-secret-keys` works. No
   change needed.
4. **`systemctl` calls in `dot_shell/zsh/12-gpg.zsh`.** The file calls
   `systemctl --user import-environment` twice. The command does not
   exist on macOS. The shell writes the error to `/dev/null`, so the
   shell still starts. After `gpgconf --kill gpg-agent`, launchd must
   start the agent again.

   **Verified on 2026-11-03.** The agent restarts on the next `gpg`
   call, so the socket returns without launchd.
5. **The OpenCode shell.** `dot_config/opencode/opencode.jsonc` pins
   `"shell": "/usr/bin/bash"`. On macOS that is bash 3.2. Point it at
   `/opt/homebrew/bin/bash` if the host has a newer bash.

   **Corrected on 2026-11-03.** macOS 26 has no `/usr/bin/bash` at all.
   The host has `/bin/bash` (3.2.57) and `/opt/homebrew/bin/bash`
   (5.3.20). OpenCode falls back to the Homebrew build at run time, so
   the shell works. The pin is still wrong.
6. **`date -Iseconds`.** The script
   `.chezmoiscripts/run_onchange_init-shellx-store.sh` uses it. BSD date
   rejects the flag and writes an error to stderr. The script continues,
   because a command substitution that fails inside an argument does not
   stop the script. Use `date +%FT%T` to remove the error.

   **Stale on 2026-11-03.** `/bin/date -Iseconds` on this host returns
   `2026-11-03T11:44:27+07:00` and exits 0. macOS 26 ships a `date`
   that supports the flag. No change needed.
7. **The legacy store.** `dot_shell/private_store/` still deploys
   `~/.shell/store/personal-laptop_environment_store.json`. No helper
   reads it now. The plan at
   `docs/plans/2026-11-01-shellx-helper-optimization.md` keeps it until
   the owner makes sure that no secret is lost.
8. **The nordvpn prompt segment.** `dot_p10k.zsh` carries a nordvpn
   segment. The file marks it as "linux only". p10k skips a segment whose
   command does not exist, so this is cosmetic.

   **Also stale.** The live `~/.p10k.zsh` is the 2026-06-18 wizard
   output. The repo file is the 2026-05-24 output. Applying moves the
   prompt backwards.
9. **The pacman module.** `dot_zshrc.tmpl` loads the prezto `pacman`
   module on Linux only. The module only adds aliases, so this is
   cosmetic. The macOS rendering loads `osx` and `command-not-found`
   instead. The reasoning is in
   [`../../docs/how-to/prezto-modules-per-os.md`](../../docs/how-to/prezto-modules-per-os.md).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| The apply stops on an encrypted file | the age identity is missing | copy `personal_pq.secret.key` into `.encryption_keys/` on the host. Not on this host. See [`macos-apply-blockers.md`](macos-apply-blockers.md). |
| The apply stops on `.shell/store/...` | `check_decrypt.sh` mapped the source-state attributes on the file name only, not on a directory component | fixed in the source tree. Run `bash .shell_helper/test_check_decrypt.sh` to confirm the mapping still matches `chezmoi target-path`. See [`macos-apply-blockers.md`](macos-apply-blockers.md). |
| The apply stops on `map has no entry for key "nonce"` | the config file predates the nonce | run `chezmoi init` |
| `gpg` reports a missing pinentry, or a prompt never appears | `gpg-agent.conf` names a path that does not exist, or a GUI dialog is waiting on a screen the caller cannot see | run `chezmoi apply` again; check `command -v pinentry-mac`; over SSH export `PINENTRY_USER_DATA=USE_CURSES=1` |
| The proxy does not answer on port 8099 | the launchd agent did not load | run `launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` and read `~/.local/state/embedding-dimensions-proxy/proxy.log` |
| The proxy is down after the launchd cleanup | the live agent was removed on 2026-11-03, before the apply | the apply installs the repo plist and the chezmoi script bootstraps it. See blocker 1 in [`macos-apply-blockers.md`](macos-apply-blockers.md) |
| The shell has no SDKMAN and no OpenBLAS flags | the apply replaced the `~/.shell/useropts/` layer with the repo `~/.shell/zsh/` layer | see blocker 2 in [`macos-apply-blockers.md`](macos-apply-blockers.md) |
| `OPENROUTER_API_OPENCODE_INDEX` is unset | the shellx store does not exist on this host | see blocker 3 in [`macos-apply-blockers.md`](macos-apply-blockers.md) |
| `~/.ssh` is mode 0755 after the apply | the repo source dir has no `private_` attribute | see blocker 6 in [`macos-apply-blockers.md`](macos-apply-blockers.md) |
| The proxy answers HTTP 502 | the provider did not answer | read the log. The proxy forwards the error text. |
| The tmux copy binding does nothing | `pbcopy` is not on the PATH of the tmux client | check `command -v pbcopy` in the same shell |
| A search returns no semantic rows | the stored rows keep the old vector width | let the tools re-embed, or delete the rows under the old model id |
| `chezmoi apply` reports a script failure | the run script could not start the service | read the stderr line that starts with `[embeddings-proxy]` |

## How chezmoi handles an OS difference

The repo uses three levers. Use the same three when you add a file.

1. A template branch inside a `.tmpl` file, for a file that both systems
   share. The variables are `.chezmoi.os` (`linux` or `darwin`),
   `.chezmoi.homeDir`, and `.chezmoi.username`.
2. An OS branch in `.chezmoiignore`, for a whole directory that belongs to
   one OS only. The patterns match the target path, not the source path. A
   pattern such as `.config/systemd` names the directory in `$HOME`. Ignore
   the directory, not the file inside it: chezmoi still creates the parent
   directories of an ignored file.
3. A runtime check in a shell file, for a path that the OS itself
   resolves. The JetBrains Toolbox scripts use this lever.

## See also

- [`macos-apply-blockers.md`](macos-apply-blockers.md) — the blockers
- [`macos-apply-target-state.md`](macos-apply-target-state.md) — the changed targets
- [`macos-apply-caveats.md`](macos-apply-caveats.md) — the changes that do not block
- [`macos-apply-fixed.md`](macos-apply-fixed.md) — the defects the apply exposed, and the fix for each one
- `docs/reports/2026-11-03-macos-host-portability.md` — the report for human readers
- `docs/how-to/embedding-dimensions-proxy-deployment.md` — the proxy guide for both systems
- `.agents/skills/chezmoi/SKILL.md` — the source-state conventions of this repo
