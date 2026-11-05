---
status: open
severity: major
captured: 2026-11-03
---

# The dotfiles source state assumed one Linux host

## Summary

This repo was written for a single Linux machine. Several files carried
Linux paths, Linux commands, or Linux service files. A macOS host could
not use them.

Commit `f855bab` fixed the parts that a macOS host breaks on. The shared
files now adapt to the operating system. The Linux-only helpers left the
target state. The macOS service files arrived.

The source change is complete. The macOS host still needs three things
from you: the age encryption key, one `chezmoi apply`, and a decision on
the pinentry tooling. The details are at the end of this file. The brief
for an agent that works on the macOS host is at
`.agents/docs/macos-host-handoff.md`.

**Update, 2026-11-03.** A later audit of the apply itself found six
blockers that this file does not cover, and it corrected one instruction
below. The age encryption key must **not** go on the macOS work laptop.
Read [`2026-11-03-macos-apply-audit/`](2026-11-03-macos-apply-audit/)
before the apply. That report holds the blockers, the decisions taken on
each, and the tooling written to make the apply reversible. The
agent-facing notes are `.agents/docs/macos-apply-blockers.md` and
`.agents/docs/macos-apply-target-state.md`.

## Impact

On a macOS host, before the change:

- The proxy for the local embeddings service had no service file, because
  the repo carried only the systemd unit for Linux.
- The GnuPG agent pointed its `pinentry-program` at a path that the
  macOS home directory does not have. Every gpg operation failed.
- The Git configuration included a work directory that the macOS home
  directory does not have. Git ignored the include without an error.
- The tmux copy binding piped the selection into `wl-copy`, a Wayland
  tool. macOS has no such command.
- The JetBrains Toolbox scripts were missing, because `~/.zprofile` holds
  a hardcoded Linux home path.

This last fault also affects Linux. The JetBrains Toolbox scripts were
missing from an interactive shell that did not start as a login shell.
A new tab in some terminal setups, and any zsh that a program starts,
reads `~/.zshrc` but not `~/.zprofile`.

After the change, a macOS host receives these parts:

- a shell setup that loads the Toolbox scripts in every interactive shell
- a tmux clipboard binding that uses `pbcopy`
- a gpg agent that starts
- a launchd service for the embeddings proxy

## Environment

| Item | Value |
|---|---|
| Repo | `~/.local/share/chezmoi` (the chezmoi source state) |
| chezmoi | 2.70.4 or newer |
| Encryption | age, recipients in `.encryption_keys/*.public.key` |
| Linux host | systemd user units, Wayland |
| macOS host | launchd, `pbcopy`, Homebrew paths under `/opt/homebrew` |

## Steps to reproduce

On a macOS host with the source state from before the change, run these
checks. Each one shows one of the faults.

1. The proxy has no service file.

   ```sh
   ls ~/.config/systemd/user/embedding-dimensions-proxy.service
   ls ~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist
   ```

2. The gpg agent points at a path that does not exist.

   ```sh
   grep pinentry-program ~/.gnupg/gpg-agent.conf
   ls ~/.shell/helper/pinentry-wrapper
   ```

3. The Git include names a path that does not exist.

   ```sh
   grep includeIf ~/.gitconfig
   ```

4. The tmux binding names a command that does not exist.

   ```sh
   grep copy-pipe-and-cancel ~/.config/tmux/tmux.conf
   command -v pbcopy
   command -v wl-copy
   ```

5. The Toolbox path is absent from an interactive shell.

   ```sh
   grep JetBrains ~/.zprofile
   zsh -c 'print -r -- $path' | tr ':' '\n' | grep Toolbox
   ```

## Expected

After the change, and after `chezmoi apply` on the macOS host:

- `chezmoi ignored` lists the launchd plist and the three pinentry paths.
  It does not list the systemd unit.
- `chezmoi cat ~/.config/tmux/tmux.conf` shows
  `copy-pipe-and-cancel "pbcopy"`.
- `chezmoi cat ~/.gitconfig` shows `gitdir:/Users/<name>/Work/`.
- `chezmoi cat ~/.gnupg/gpg-agent.conf` shows a `pinentry-program` line that
  names `pinentry-mac` when the binary exists, and no line when it is
  missing.
- `launchctl print "gui/$(id -u)/com.user.embedding-dimensions-proxy"`
  shows the agent with a state and a process id.

> **Update, 2026-11-03, later in the day.** The macOS work laptop ran
> `chezmoi apply` against this source state. The result of the apply, and
> the fixes it exposed, are in
> [`2026-11-03-macos-apply-audit/`](2026-11-03-macos-apply-audit/).

## Actual

The macOS host did not run `chezmoi apply` with the new source state.
The expected list above is the target state that the source state
describes. The Linux host still runs the old target state, because
`chezmoi apply` is a separate step from the source edit.

## What changed

| Source file | Before | After | Reason |
|---|---|---|---|
| `dot_shell/helper/executable_runpriv.tmpl` | deployed `~/.shell/helper/runpriv` | removed from the repo | shellx replaced it. The file used `sha512sum` and `openssl enc -chacha20`, which macOS does not have. |
| `dot_shell/helper/executable_encrypt_store.sh.tmpl` | deployed `~/.shell/helper/encrypt_store.sh` | removed from the repo | the same reason |
| `dot_shell/zsh/completions/_runpriv.tmpl` | deployed `_runpriv` | removed from the repo | the completion belongs to the removed helper |
| `dot_shell/zsh/10-common-export.zsh` | a runpriv PATH comment | the shellx helper PATH plus the JetBrains Toolbox scripts PATH | the Toolbox line was in `~/.zprofile`, which only a login shell reads. The new loop accepts the Linux path and the macOS path. |
| `dot_zprofile` | a Toolbox PATH export with the hardcoded path `/home/ardhinata/.local/share/JetBrains/Toolbox/scripts` | sources `~/.profile` only | the Toolbox line moved to the zsh file, so an interactive shell without a login session also gets the scripts |
| `dot_config/tmux/tmux.conf` | a plain file | `dot_config/tmux/tmux.conf.tmpl` | the clipboard bridge now names `pbcopy` on macOS and `wl-copy` on Linux |
| `dot_gitconfig` | a plain file with `/home/ardhinata/Work/` | `dot_gitconfig.tmpl` with `{{ .chezmoi.homeDir }}/Work/` | the home path differs between the two hosts |
| `private_dot_gnupg/private_gpg-agent.conf` | a plain file with `pinentry-program .../pinentry-wrapper` | `private_dot_gnupg/private_gpg-agent.conf.tmpl` without that line | the wrapper is no longer deployed, so the line pointed at a missing file |
| `.chezmoiignore` | no operating system branch | a branch for the systemd directory and the launchd directory, plus three pinentry paths | the file matches target paths. The pattern names the directory, not the unit file, because chezmoi still creates the parent directories of an ignored file. |
| `Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist.tmpl` | absent | added | the macOS service for the embeddings proxy |
| `.chezmoiscripts/run_start-embeddings-proxy.sh` | absent | added | starts the service of the host operating system on every apply |
| `dot_shell/helper/executable_pinentry-switch`, `dot_shell/helper/executable_pinentry-wrapper`, `dot_shell/zsh/completions/_pinentry-switch` | deployed | excluded from the target state | nothing points at them any more. The sources stay in the repo. |

The `Library` source directory carries no `dot_` prefix. The prefix adds
a dot at the front, which would give `~/.Library/LaunchAgents/` instead of
`~/Library/LaunchAgents/`.

## What still assumes Linux

1. **The age encryption key.** `.encryption_keys/personal_pq.secret.key`
   is not in git.

   **Corrected on 2026-11-03.** Do **not** copy the identity to the macOS
   work laptop. The encrypted files are the personal machine's SSH keys.
   The host stays separate. The `check_decrypt.sh` mechanism skips the
   encrypted files the host cannot decrypt, so the apply succeeds with no
   identity. See `.agents/docs/macos-apply-blockers.md`.
2. **The pinentry sources.** The switcher and the wrapper name
   `/usr/bin/pinentry-*` and use `ldd`. Homebrew GnuPG installs the
   binaries in `/opt/homebrew/bin`, and macOS has no `ldd`. The change
   excludes these two files from the target state instead of fixing
   them. Decide whether the macOS host needs them.
3. **`use-keyboxd`.** `private_dot_gnupg/common.conf` sets it. Homebrew
   GnuPG 2.4 supports it, but the keyboxd daemon must run.
4. **`systemctl` calls in `dot_shell/zsh/12-gpg.zsh`.** The file calls
   `systemctl --user import-environment` twice. The command does not
   exist on macOS. The shell writes the error to `/dev/null`, so the
   shell still starts.
5. **The OpenCode shell.** `dot_config/opencode/private_opencode.jsonc`
   pins the shell as `"shell": "bash"`. On macOS that resolves through
   PATH. The host has `/opt/homebrew/bin/bash` (5.3.20) ahead of
   `/bin/bash` (3.2.57).
6. **`date -Iseconds`.** The script
   `.chezmoiscripts/run_onchange_init-shellx-store.sh` uses it. BSD date
   rejects the flag and writes an error to stderr. The script continues,
   because a command substitution that fails inside an argument does not
   stop the script.
7. **The legacy store.** `dot_shell/private_store/` still deploys
   `~/.shell/store/personal-laptop_environment_store.json`. No helper
   reads it now. The plan at
   `docs/plans/2026-11-01-shellx-helper-optimization.md` keeps it until
   the owner makes sure that no secret is lost.
8. **Cosmetic items.** `dot_p10k.zsh` carries a nordvpn segment that the
   file marks as "linux only", and `dot_zshrc` loads the prezto `pacman`
   module. p10k skips a segment whose command does not exist, and the
   pacman module only adds aliases.

> **Update, 2026-11-03.** The `dot_zshrc` file is now a template named
> `dot_zshrc.tmpl`, and the `pacman` module moved to the Linux branch of
> it. The macOS branch loads `osx` and `command-not-found` instead. See
> [`../how-to/prezto-modules-per-os.md`](../how-to/prezto-modules-per-os.md).
> The rest of this report describes the state at the time of capture.

## Workaround

A macOS host can work without the pinentry tools, because gpg-agent
uses its built-in default pinentry when the configuration names none.
The switcher and the wrapper stay out of the target state, so the
host has no way to change the pinentry backend. A host that needs the
choice must patch the two source files and drop the ignore lines.

> **Update, 2026-11-03, later in the day.** The pinentry tooling is Linux
> only. The ignore block in `.chezmoiignore` and the `gpg-agent.conf`
> template branch on `.chezmoi.os`. Linux keeps the wrapper as the
> `pinentry-program` of gpg-agent. A macOS host with `pinentry-mac` on
> PATH now renders `pinentry-program <lookPath pinentry-mac>` instead of
> no line, so the GUI dialog works without a TTY; a host without the
> binary keeps the compiled default.
> The rest of this report describes the state at the time of capture.

## Related

| Path | Holds |
|---|---|
| `.agents/docs/macos-host-handoff.md` | the brief for an agent that works on the macOS host |
| `docs/how-to/embedding-dimensions-proxy-deployment.md` | the proxy guide for both systems |
| `docs/plans/2026-11-01-shellx-helper-optimization.md` | the plan that retires the runpriv helper |
| `.agents/skills/chezmoi/SKILL.md` | the source-state conventions of this repo |
