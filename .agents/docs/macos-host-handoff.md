# macOS host handoff

Read this file when you work on the macOS host of this dotfiles repo. It
names the state of the source tree, the files that the macOS host receives,
and the parts that still assume Linux. The report for human readers lives
at `docs/reports/2026-11-03-macos-host-portability.md`.

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

chezmoi does not delete a file that it no longer manages. A copy of
`~/.shell/helper/runpriv` or `~/.shell/helper/encrypt_store.sh` stays on
disk after an apply. Remove it by hand on both hosts.

## Steps to verify the macOS host

Run these on the macOS host after `chezmoi apply`.

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
| `chezmoi ignored` | lists `Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` and the three pinentry paths. It does not list the systemd unit. |
| `chezmoi cat ~/.config/tmux/tmux.conf` | shows `copy-pipe-and-cancel "pbcopy"` |
| `chezmoi cat ~/.gitconfig` | shows `gitdir:/Users/<name>/Work/` |
| `chezmoi cat ~/.gnupg/gpg-agent.conf` | shows no `pinentry-program` line |
| `launchctl print` | shows the agent with a state and a process id |

## Open items to patch

1. **The age identity.** `.encryption_keys/personal_pq.secret.key` is not
   in git. Put it on the macOS host before the first apply, or the apply
   fails on every encrypted file.
2. **The pinentry sources.** `executable_pinentry-switch` and
   `executable_pinentry-wrapper` name `/usr/bin/pinentry-*` and use `ldd`.
   Homebrew GnuPG installs the binaries in `/opt/homebrew/bin`, and macOS
   has no `ldd`. Patch both files, then remove the three ignore lines
   from `.chezmoiignore`.
3. **`use-keyboxd`.** `private_dot_gnupg/common.conf` sets it. Homebrew
   GnuPG 2.4 supports it, but the keyboxd daemon must run. Remove the
   line if `gpg` reports a keyboxd error.
4. **`systemctl` calls in `dot_shell/zsh/12-gpg.zsh`.** The file calls
   `systemctl --user import-environment` twice. The command does not
   exist on macOS. The shell writes the error to `/dev/null`, so the
   shell still starts. After `gpgconf --kill gpg-agent`, launchd must
   start the agent again.
5. **The OpenCode shell.** `dot_config/opencode/opencode.jsonc` pins
   `"shell": "/usr/bin/bash"`. On macOS that is bash 3.2. Point it at
   `/opt/homebrew/bin/bash` if the host has a newer bash.
6. **`date -Iseconds`.** The script
   `.chezmoiscripts/run_onchange_init-shellx-store.sh` uses it. BSD date
   rejects the flag and writes an error to stderr. The script continues,
   because a command substitution that fails inside an argument does not
   stop the script. Use `date +%FT%T` to remove the error.
7. **The legacy store.** `dot_shell/private_store/` still deploys
   `~/.shell/store/personal-laptop_environment_store.json`. No helper
   reads it now. The plan at
   `docs/plans/2026-11-01-shellx-helper-optimization.md` keeps it until
   the owner makes sure that no secret is lost.
8. **The nordvpn prompt segment.** `dot_p10k.zsh` carries a nordvpn
   segment. The file marks it as "linux only". p10k skips a segment whose
   command does not exist, so this is cosmetic.
9. **The pacman module.** `dot_zshrc` loads the prezto `pacman` module.
   The module only adds aliases, so this is cosmetic.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| The apply stops on an encrypted file | the age identity is missing | copy `personal_pq.secret.key` into `.encryption_keys/` on the host |
| `gpg` reports a missing pinentry | the host has a stale `gpg-agent.conf` with a `pinentry-program` line | run `chezmoi apply` again, or remove the line by hand |
| The proxy does not answer on port 8099 | the launchd agent did not load | run `launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` and read `~/.local/state/embedding-dimensions-proxy/proxy.log` |
| The proxy answers HTTP 502 | the provider did not answer | read the log. The proxy forwards the error text. |
| The tmux copy binding does nothing | `pbcopy` is not on the PATH of the tmux client | check `command -v pbcopy` in the same shell |
| A search returns no semantic rows | the stored rows keep the old vector width | let the tools re-embed, or delete the rows under the old model id |
| `chezmoi apply` reports a script failure | the run script could not start the service | read the stderr line that starts with `[embeddings-proxy]` |

## How chezmoi handles an OS difference

The repo uses three levers. Use the same three when you add a file.

1. A template branch inside a `.tmpl` file, for a file that both systems
   share. The variables are `.chezmoi.os` (`linux` or `darwin`),
   `.chezmoi.homeDir`, and `.chezmoi.username`.
2. An OS branch in `.chezmoiignore`, for a whole file that belongs to one
   OS only. The patterns match the target path, not the source path. A
   pattern such as `.config/systemd/user/x.service` names the file in
   `$HOME`.
3. A runtime check in a shell file, for a path that the OS itself
   resolves. The JetBrains Toolbox scripts use this lever.

## See also

- `docs/reports/2026-11-03-macos-host-portability.md` — the report for human readers
- `docs/how-to/embedding-dimensions-proxy-deployment.md` — the proxy guide for both systems
- `.agents/skills/chezmoi/SKILL.md` — the source-state conventions of this repo
