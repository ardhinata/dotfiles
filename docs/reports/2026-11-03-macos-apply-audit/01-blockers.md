# The six blockers on the macOS work laptop

Each blocker states what breaks, how it was verified, and who owns the
remaining work.

**Status: open.** Blocker 1 is done. Blockers 2, 3 and 5 are with the
owner. Blocker 4 is done. Blocker 6 was accepted as a known cost.

Back to the [report index](README.md).

## Blocker 1: two proxy agents fight for port 8099

**Status: resolved on 2026-11-03.**

The live agent carried the label `com.ardhinata.embedding-dimensions-proxy`.
The repo template renders `com.user.embedding-dimensions-proxy`. An apply
**adds** the new plist. It does not remove the old one, because chezmoi
only removes files it manages.

Both agents set `KeepAlive` and both bind `127.0.0.1:8099`. The second
one cannot bind. `ThreadingHTTPServer` sets `allow_reuse_address`, so the
bind still fails with `EADDRINUSE`. Verified on a scratch port:

```text
first listener holds 18099
second listener FAILED: OSError [Errno 48] Address already in use
```

The live agent keeps the port. The new agent crash-loops in the
background, and the chezmoi script
`.chezmoiscripts/run_start-embeddings-proxy.sh` bootstraps it on every
apply.

What was done:

```bash
launchctl bootout "gui/$(id -u)/com.ardhinata.embedding-dimensions-proxy"
rm ~/Library/LaunchAgents/com.ardhinata.embedding-dimensions-proxy.plist
```

The plist and the live proxy script are backed up at
`~/.local/state/chezmoi-host-artifacts/`. The proxy stays down until the
apply installs the repo plist and the chezmoi script bootstraps it.

Two behaviour changes come with the repo version. The repo script serves
a per-caller vector width, where the live one served a fixed width. The
repo plist routes to `{"only":["nebius","deepinfra"]}`, where the live
plist routed to `{"order":["deepinfra","siliconflow"]}`.

The repo plist relies on the script shebang. launchd reads no `PATH`, so
`#!/usr/bin/env python3` resolves to the system Python 3.9.6 rather than
the Homebrew 3.15.2. The repo proxy script compiles under 3.9 and its
test suite passes there, with 22 tests. This is safe.

## Blocker 2: the apply replaces the live shell setup

**Status: open. The owner migrates by hand.**

The live `~/.zshrc` and `~/.zprofile` are symlinks into `~/.shell/`. The
repo deploys plain files. The live `~/.shell/.zshrc` sources
`~/.shell/useropts/`. The repo `dot_zshrc` sources `~/.shell/zsh/`. Two
different layouts.

The gap is 11 items, not 3. Each row below names the repo file to
change.

| Missing from the repo | Where it lives now | Repo file to change |
|---|---|---|
| `00-brew-fix.zsh`, the awscli `DYLD_LIBRARY_PATH` patch | `~/.shell/useropts/` | new `dot_shell/zsh/13-brew-fix.zsh` |
| `01-openblas.zsh`, the `LDFLAGS` and `PKG_CONFIG_PATH` exports | `~/.shell/useropts/` | new `dot_shell/zsh/11-openblas.zsh` |
| `99-sdkman.zsh`, the SDKMAN init | `~/.shell/useropts/` | new `dot_shell/zsh/99-sdkman.zsh` |
| `brew shellenv` | `~/.shell/.zprofile` | `dot_shell/zsh/10-common-export.zsh` |
| `HOMEBREW_CASK_OPTS="--appdir=~/Applications"` | `~/.shell/.zshrc` | `dot_shell/zsh/10-common-export.zsh` |
| The Kiro CLI pre and post blocks | `~/.shell/.zshrc`, `~/.shell/.zprofile` | `dot_zshrc`, `dot_zprofile` |
| The bun `_bun` completions | `~/.shell/.zshrc` | `dot_shell/zsh/10-common-export.zsh` |
| The prezto `command-not-found`, `homebrew` and `gnu-utility` modules | `~/.shell/useropts/00-zgenom.zsh` | `dot_zshrc` |
| `zgenom prezto "git:log:context" format "medium"` | `~/.shell/useropts/00-zgenom.zsh` | `dot_zshrc` |
| `zgenom prezto "homebrew:alias" skip "yes"` | `~/.shell/useropts/00-zgenom.zsh` | `dot_zshrc` |
| The brew `site-functions` on `fpath` | `~/.shell/useropts/03-compinit.zsh` | `dot_shell/zsh/00-before-zgenom.zsh` |

Without the first three rows, SDKMAN and OpenBLAS stop working and the
awscli patch is gone.

The repo shell has more than the live one. `dot_shell/zsh/10-common-export.zsh`
adds `EDITOR`, the `shellx` helper directory, the JetBrains Toolbox
scripts for both operating systems, and `fnm`.

Two ordering traps sit in the migration. The repo `dot_zshrc` sources
the `dot_shell/zsh/` files in numeric order. `00-brew-fix.zsh` calls
`brew --prefix`, so it must come after `10-common-export.zsh` puts
Homebrew on the PATH. Rename it `13-brew-fix.zsh`. And the live file
sources `99-sdkman.zsh` before `03-compinit.zsh`, so the numeric order is
not the live order.

One line must not be ported. The live `00-zgenom.zsh` runs
`zgenom compile "${_SHELL_DIR}"`, a recursive compile. The repo
deliberately does not, because stale `.zwc` bytecode shadows source edits.

The live files are backed up at `~/.local/state/chezmoi-host-artifacts/`:

| Backup path | Live source |
|---|---|
| `shell/.zshrc` | `~/.shell/.zshrc` |
| `shell/.zprofile` | `~/.shell/.zprofile` |
| `shell/.zshenv` | `~/.shell/.zshenv` |
| `shell/useropts.tar` | `~/.shell/useropts/`, all 7 files |

`~/.zshenv` holds the Jira and Bitbucket tokens in plaintext. The repo
has no `dot_zshenv`, so chezmoi does not manage it and the file survives
the apply untouched.

## Blocker 3: the shellx store does not exist on this host

**Status: open. The owner owns this.**

The live `~/.shell/.zshrc` sets `OPENROUTER_API_OPENCODE_INDEX` directly.
The repo `dot_shell/zsh/20-secret-env-load.zsh` loads it from the shellx
store instead. The store path is derived from the master key, and the
master key is derived from the nonce:

```text
master key = sha256("com.ardju.utils:shellx:" + nonce)
store slug = blake2b(master_key, 16)
store path = ~/.local/share/<slug>/
```

After `chezmoi init`, the nonce on this host is
`4RTUdw6xmQCCcMpmJPGvbhRMdOjsNWhCzjeFXb9s4N8TXnTmkBydzaioGPh1GNuk`. It
derives the master key
`10a05109a2703926a1a06f579343d1cc56d7590ed23da2bac4026f64e53396f1` and
the store path `~/.local/share/6d8ec0bef890c2df4bfb647d41bfc7d1/`.

Neither the store nor the legacy `~/.shellx-store` marker exists here, so
no store was ever created on this host. The apply creates the master key
file, but it creates no store. The chezmoi script
`.chezmoiscripts/run_onchange_init-shellx-store.sh` only ensures
`~/.local/share` exists, sets it to mode 0700, and fixes the modes of an
existing store.

So `shellx env OPENROUTER_API_OPENCODE_INDEX` fails, the helper prints a
warning, and the variable stays unset. The `cortexkit` configs read the
key from the environment, so the AFT index and the magic context lose
their key.

The repo export would decrypt the store, but not here. The export file
`.encrypted_data/env_store/encrypted_shiraki-yuki_621ef85e973ed2676f8c5de1a89d27e8_20261101T171251Z.jsonc.age`
is encrypted to two recipients, `master_pq` and `personal_pq`. The
`shellx import` command calls `chezmoi decrypt` under the hood, so it
needs one of those identities. This host has no age identity.

The slug in the export file name does not match the new nonce, but that
does not block the import. `shellx import` reads the target slug from
`_read_slug()`. That function falls back to the derived slug when no
`.sl` file exists, and it names the blobs with that slug. The file name
slug is informational.

The practical fix on this host is to carry the single
`OPENROUTER_API_OPENCODE_INDEX` export over into the repo shell. The live
value is on line 56 of `~/.shell/.zshrc`, and a copy sits in the backup
at `~/.local/state/chezmoi-host-artifacts/shell/.zshrc`.

## Blocker 4: the live config predates the nonce

**Status: done on 2026-11-03. The owner ran `chezmoi init`.**

The live config had no `system_environment.nonce`, so the master key
template failed and every chezmoi command that rendered the target state
failed. The error text is in the [report index](README.md).

`chezmoi init` regenerates the config. It prompts for the profile and
generates a random nonce when the existing value is not 64 characters.
A new nonce means a new master key, so the init had to happen before any
store import. It did.

`chezmoi status` now returns 53 targets, and `chezmoi cat
~/.local/share/shellx/master.key` renders the master key.

## Blocker 5: the repo signing keys are not in the local keyring

**Status: open. The owner restores the keys.**

The repo `dot_gitconfig` sets `signingkey = 0x330FE76C4FD0F3BC`. The repo
`dot_gnupg/gpg.conf` sets `default-key 9909A0802A11B93F`. The live
`~/.gitconfig` uses `0x32A87E6BED04FEC6`, which is present.

Verified after `chezmoi init`: neither repo key is in the keyring. Only
`32A87E6BED04FEC6` is. There is no key backup under `~/.gnupg/` or
`~/.local/state/`, so the backup is elsewhere.

The apply points git at a key that cannot sign. Git falls back to the
default key, so commits stop being signed with the intended identity.

## Blocker 6: the apply widens the mode on three directories

**Status: accepted on 2026-11-03. The apply runs as-is.**

This is not a hard blocker. The apply succeeds and SSH keeps working.
OpenSSH checks the private key files and `authorized_keys`, not the
`~/.ssh` directory mode. A key file must not be readable by group or
others, and `authorized_keys` must not be writable by others. `0755` on
the directory is neither.

The apply changes no key file mode on this host. The 15 `~/.ssh/keys/*`
files stay encrypted and skipped, the live key files stay `0600`, and
`authorized_keys` stays `0600`.

Three directories end up wider:

| Path | Change |
|---|---|
| `~/.ssh` | `0700` to `0755` |
| `~/.config/cortexkit` | `0700` to `0755` |
| `~/Library` | `0700` to `0755` |

`~/Library` is the most exposed of the three, because it opens the whole
tree of app data and `Application Support`.

The fix is a rename in the source tree. The repo source dir is `dot_ssh`,
which carries no `private_` attribute. Verified chezmoi behaviour, with
a scratch source tree:

| Source | Target mode |
|---|---|
| `dot_ssh` | `0755` |
| `private_dot_ssh` | `0700` |
| `private_dot_ssh/private_config.d` | `0700` |
| `dot_config/private_cortexkit` | `0700` |

`private_` applies to one path component only. It does not propagate to
nested directories, so each directory that must end up `0700` needs its
own prefix. The renames would be:

| Current | New |
|---|---|
| `dot_ssh` | `private_dot_ssh` |
| `dot_ssh/config.d` | `private_dot_ssh/private_config.d` |
| `dot_ssh/keys` | `private_dot_ssh/private_keys` |
| `dot_config/cortexkit` | `dot_config/private_cortexkit` |
| `Library` | `private_Library` |

The owner chose to skip the renames and apply as-is. The wide modes
stay. If they are fixed later, rename the source dirs and re-apply.

## What the apply still changes

The blockers cover what breaks. They do not cover every change. The
non-blocking changes are in
[`.agents/docs/macos-apply-caveats.md`](../../../.agents/docs/macos-apply-caveats.md),
and the full list of 53 targets is in
[`.agents/docs/macos-apply-target-state.md`](../../../.agents/docs/macos-apply-target-state.md).

The two that matter most:

- The cc-safety-net policy gets **tighter**. The repo policy removes
  overrides that say `off`, which turns the rules on. The repo
  `opencode.jsonc` also drops four `rm` deny patterns. So `rm -rf` inside
  the working directory is no longer blocked by the OpenCode permission
  layer. The personal `destructive-actions.md` rule still asks for
  approval.
- The AFT index rebuilds. `dot_config/cortexkit/aft.jsonc` changes the
  identity salt and the vector width, so the 688 MB index in
  `~/.local/share/cortexkit` rebuilds. It needs the OpenRouter key from
  blocker 3.
