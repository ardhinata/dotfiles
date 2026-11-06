# macOS apply blockers

The verified blockers that stop a `chezmoi apply` on the macOS work laptop.

Companions:

- [`macos-apply-target-state.md`](macos-apply-target-state.md) holds the
  53 changed targets and the decisions each one needs.
- [`macos-apply-caveats.md`](macos-apply-caveats.md) holds the changes
  that do not block but narrow a permission or downgrade a file.
- [`macos-apply-fixed.md`](macos-apply-fixed.md) holds the defects the
  apply exposed, with the fix for each one.

All findings were verified on 2026-11-03 with chezmoi v2.74.0 against the
live host.

## Blocker 1: the launchd agent label changed, so two proxies fight for port 8099

**Resolved on 2026-11-03.** The live agent was stopped and deleted, so the
repo agent is the only one.

The live agent was `com.ardhinata.embedding-dimensions-proxy`. The repo
template renders `com.user.embedding-dimensions-proxy`. The apply would
have **added** the new plist without removing the old one, because chezmoi
only removes files it manages. Both agents use `KeepAlive` and both bind
`127.0.0.1:8099`. `ThreadingHTTPServer` sets `allow_reuse_address`, so the
second bind still fails with `EADDRINUSE`. Verified:

```
first listener holds 18099
second listener FAILED: OSError [Errno 48] Address already in use
```

What was done:

```bash
launchctl bootout "gui/$(id -u)/com.ardhinata.embedding-dimensions-proxy"
rm ~/Library/LaunchAgents/com.ardhinata.embedding-dimensions-proxy.plist
```

The plist and the live proxy script are backed up at
`~/.local/state/chezmoi-host-artifacts/`. The proxy is down until the
apply. The apply installs the repo plist and the repo script, then
`.chezmoiscripts/run_start-embeddings-proxy.sh` bootstraps the agent.

Two differences the repo version brings. The repo script serves a
per-caller vector width, the live one served a fixed width. The repo
plist routes to `{"only":["nebius","deepinfra"]}`, the live plist routed to
`{"order":["deepinfra","siliconflow"]}`.

The repo plist relies on the script shebang. launchd reads no `PATH`, so
`#!/usr/bin/env python3` resolves to the system Python 3.9.6. The repo
script compiles under 3.9 and its test suite passes there (22 tests), so
this is safe.

## Blocker 2: the apply replaces the live zsh setup with a different layout

The live `~/.zshrc` and `~/.zprofile` are symlinks into `~/.shell/`. The
repo deploys plain files. The diff shows both:

```
diff --git a/.zshrc b/.zshrc
deleted file mode 120755
--- a/.zshrc
+++ b/.zshrc
-.shell/.zshrc
```

The live `~/.shell/.zshrc` sources `~/.shell/useropts/`. The repo
`dot_zshrc.tmpl` sources `~/.shell/zsh/`. Two different layouts.

**The migration is manual.** The live files are backed up at
`~/.local/state/chezmoi-host-artifacts/`:

| Backup path | Live source |
|---|---|
| `shell/.zshrc` | `~/.shell/.zshrc` |
| `shell/.zprofile` | `~/.shell/.zprofile` |
| `shell/.zshenv` | `~/.shell/.zshenv` |
| `shell/useropts.tar` | `~/.shell/useropts/` (all 7 files) |
| `shell/embedding_dimensions_proxy.py` | the live proxy script |

`~/.zshenv` is a symlink to `~/.shell/.zshenv`. The repo has no
`dot_zshenv`, so chezmoi does not manage it. The file holds the Jira and
Bitbucket tokens in plaintext and survives the apply untouched.

### What the live shell has and the repo shell does not

Each row needs a decision. The repo file to change is in the third column.

| Missing from the repo | Where it lives now | Repo file to change |
|---|---|---|
| `00-brew-fix.zsh` (awscli `DYLD_LIBRARY_PATH` patch) | `~/.shell/useropts/` | done 2026-11-06: new `dot_shell/zsh/05-homebrew-opts.zsh` (carries `00-brew-fix.zsh` and the cask opts; the openblas/SDKMAN/bun/opencode rows are still open) |
| `01-openblas.zsh` (`LDFLAGS`, `CPPFLAGS`, `PKG_CONFIG_PATH`) | `~/.shell/useropts/` | new `dot_shell/zsh/11-openblas.zsh` |
| `99-sdkman.zsh` (SDKMAN init) | `~/.shell/useropts/` | new `dot_shell/zsh/99-sdkman.zsh` |
| `brew shellenv` | `~/.shell/.zprofile` | done: `dot_shell/zsh/00-before-zgenom.zsh` |
| `HOMEBREW_CASK_OPTS="--appdir=~/Applications"` | `~/.shell/.zshrc` | done 2026-11-06: `dot_shell/zsh/05-homebrew-opts.zsh` |
| Kiro CLI pre and post blocks | `~/.shell/.zshrc`, `~/.shell/.zprofile` | `dot_zshrc.tmpl`, `dot_zshprofile` |
| bun `_bun` completions | `~/.shell/.zshrc` | `dot_shell/zsh/10-common-export.zsh` |
| prezto `command-not-found` | `~/.shell/useropts/00-zgenom.zsh` | done: `dot_zshrc.tmpl` (macOS branch) |
| prezto `homebrew` | `~/.shell/useropts/00-zgenom.zsh` | skipped on purpose, see [`../../docs/how-to/prezto-modules-per-os.md`](../../docs/how-to/prezto-modules-per-os.md) |
| prezto `gnu-utility` | `~/.shell/useropts/00-zgenom.zsh` | skipped on purpose, see [`../../docs/how-to/prezto-modules-per-os.md`](../../docs/how-to/prezto-modules-per-os.md) |
| `zgenom prezto "git:log:context" format "medium"` | `~/.shell/useropts/00-zgenom.zsh` | `dot_zshrc.tmpl` |
| `zgenom prezto "homebrew:alias" skip "yes"` | `~/.shell/useropts/00-zgenom.zsh` | not needed, the `homebrew` module is not loaded |
| brew `site-functions` on `fpath` | `~/.shell/useropts/03-compinit.zsh` | done: `dot_shell/zsh/00-before-zgenom.zsh` |

The repo sets `zgenom prezto prompt managed "yes"` and
`zgenom prezto utility:download helper "aria2c"`. The `editor` module is
now in the common list. The `pacman` module moved to the Linux branch of
`dot_zshrc.tmpl`.

### The repo shell has what the live one lacks

`dot_shell/zsh/10-common-export.zsh` adds `EDITOR`, the `shellx` helper
directory, the JetBrains Toolbox scripts for both operating systems, and
`fnm`. The live `02-opencode.zsh` cached the opencode completions in
`fpath`. The repo sources them fresh each shell.

### Two ordering rules for the migration

The repo `dot_zshrc` sources the `dot_shell/zsh/` files in numeric order.

- `00-brew-fix.zsh` calls `brew --prefix`, so it must come **after**
  the Homebrew prefix is on the PATH. `00-before-zgenom.zsh` now runs
  `brew shellenv`, so the PATH is already set. Name the file
  `13-brew-fix.zsh`, not `00-brew-fix.zsh`.
- The live file sources `99-sdkman.zsh` before `03-compinit.zsh`, so the
  numeric order is not the live order. Keep SDKMAN after the other files.

The live `00-zgenom.zsh` runs `zgenom compile "${_SHELL_DIR}"`, a
recursive compile. The repo deliberately does not, because stale `.zwc`
bytecode shadows source edits. Do not port that line.

## Blocker 2: the apply replaces the live zsh setup with a different layout

The live `~/.zshrc` and `~/.zprofile` are symlinks into `~/.shell/`. The
repo deploys plain files. The diff shows both:

```
diff --git a/.zshrc b/.zshrc
deleted file mode 120755
--- a/.zshrc
+++ b/.zshrc
-.shell/.zshrc
```

The live `~/.shell/.zshrc` sources `~/.shell/useropts/`. The repo
`dot_zshrc.tmpl` sources `~/.shell/zsh/`. Two different layouts.

The live `useropts/` files have no counterpart in the repo:

| Live file | What it does | Repo equivalent |
|---|---|---|
| `00-brew-fix.zsh` | Patches `DYLD_LIBRARY_PATH` for awscli | done 2026-11-06: `dot_shell/zsh/05-homebrew-opts.zsh` |
| `00-zgenom.zsh` | zgenom setup | `dot_zshrc.tmpl` inlines it |
| `01-openblas.zsh` | Sets `LDFLAGS`, `CPPFLAGS`, `PKG_CONFIG_PATH` | none |
| `02-bun.zsh` | bun path and completions | `10-common-export.zsh` |
| `02-opencode.zsh` | opencode completions via fpath | `10-common-export.zsh` |
| `03-compinit.zsh` | `compinit` plus brew site-functions | Prezto completion module |
| `99-sdkman.zsh` | SDKMAN init | none |

So after the apply, SDKMAN and OpenBLAS still stop working (open). The
awscli `DYLD_LIBRARY_PATH` patch was restored on 2026-11-06 in
`dot_shell/zsh/05-homebrew-opts.zsh`, together with the cask opts and
the brew python libexec PATH entry.

The repo `dot_zshrc.tmpl` also drops the Kiro CLI pre and post blocks that the
live files carry.

**Fix before apply.** Move the three unique files into the repo layout, as
`dot_shell/zsh/` files, and source them from `dot_zshrc.tmpl`. The live files
are on disk, so the content is available:

- `~/.shell/useropts/01-openblas.zsh`
- `~/.shell/useropts/00-brew-fix.zsh`
- `~/.shell/useropts/99-sdkman.zsh`

The SDKMAN file must stay last. `dot_zshrc.tmpl` sources the `dot_shell/zsh/`
files in numeric order already, so a `99-sdkman.zsh` name works.

## Blocker 3: the shellx store does not exist on this host, so the OpenRouter key is lost

The live `~/.shell/.zshrc` sets the key directly:

```zsh
export OPENROUTER_API_OPENCODE_INDEX="sk-or-v1-..."
```

The repo `dot_shell/zsh/20-secret-env-load.zsh` loads it from the shellx
store instead. shellx keeps its store at `~/.local/share/<slug>/`, where
the slug is derived from the master key, and the master key is derived from
the nonce:

```
slug = blake2b(STATIC_PW)[:16], STATIC_PW = sha256("com.ardju.utils:shellx:" + nonce)
```

Neither exists on this host. `~/.local/share/shellx/` does not exist, and
`~/.shellx-store` does not exist either, so no store was ever created here.

The apply creates `~/.local/share/shellx/master.key` from the nonce, but it
creates no store. The chezmoi script
`.chezmoiscripts/run_onchange_init-shellx-store.sh` only ensures
`~/.local/share` exists, sets it to mode 0700, and fixes the modes of an
existing store. It does not create one.

So `shellx env OPENROUTER_API_OPENCODE_INDEX` fails, the helper prints a
warning, and the variable stays unset. The `cortexkit` configs read the key
from the environment, so the AFT index and the magic context lose their
API key.

After `chezmoi init` the derived store path is
`~/.local/share/<slug>/`, with the slug from the formulas above.

The `dot_shell/private_store/` directory in the repo is the **legacy**
ejson store. It deploys `~/.shell/store/personal-laptop_environment_store.json`,
and the shellx helpers do not read it. The shellx README calls it the old
design. No helper reads that path any more.

**The import route does not work on this host.** The export in the repo is
age-encrypted to two recipients: `master_pq` and `personal_pq`. The
`shellx import` command calls `chezmoi decrypt` under the hood, so it needs
one of those identities. This host has no age identity. The
`age.identities` glob in `.chezmoi.yaml.tmpl` matches `*.secret.key`, and
the repo has no such file. It has `personal_pq.secret.key.age` and
`personal_pq.secret.key.asc`, and neither matches the glob.

The `personal_pq` identity is the personal machine's identity. Per the
host-separation policy it must not come to this work laptop.

**Owner: the user. Done on 2026-11-03.** The store was created on this host
and the key was copied into it from the live shell file:

```bash
~/.shell/helper/shellx init
python3 - <<'EOF' | ~/.shell/helper/shellx store OPENROUTER_API_OPENCODE_INDEX
import re, pathlib, sys
t = pathlib.Path.home().joinpath('.shell/.zshrc').read_text()
v = re.search(r'^export OPENROUTER_API_OPENCODE_INDEX=(.*)$', t, re.M).group(1)
sys.stdout.write(v.strip().strip('"').strip("'"))
EOF
```

The store is at `~/.local/share/<slug>/`. The
value came from line 56 of `~/.shell/.zshrc`, which the apply left in
place because chezmoi does not manage it. A fresh login shell now loads
the variable with no warning.

Note: `.encrypted_data/env_store/README.md` describes a per-profile snippet
mechanism (`<profile>_<name>.zsh.age`, sourced by
`dot_shell/zsh/00-before-zgenom.zsh`). No file in the repo implements it.
`00-before-zgenom.zsh` does not read `.encrypted_data/` at all. Only the
`shellx export` / `shellx import` flow is real.

## Blocker 4: `chezmoi init` must run first, and it prompts

The live config `~/.config/chezmoi/chezmoi.yaml` is stale. It has no
`system_environment.nonce`, so the master key template fails:

```
chezmoi: .local/share/shellx/master.key: template: ... map has no entry for key "nonce"
```

Every chezmoi command that renders the target state fails on this. The
`chezmoi status` output is empty.

`chezmoi init` regenerates the config, but it prompts for the profile
(`promptStringOnce`) and generates a **random** nonce when the existing
value is not 64 characters. The nonce decides the master key value:

```
printf '%s' "com.ardju.utils:shellx:<nonce>" | sha256sum -a 256
```

A new nonce means a new master key. That is fine on a fresh host with no
store. It must happen **before** the store import in blocker 3, or the
slug changes and the import fails.

**Fix before apply.** Run `chezmoi init` once, interactively, and record
the nonce it writes into the config. Then verify the master key renders:

```bash
chezmoi cat ~/.local/share/shellx/master.key
```

**Owner: the user. Done on 2026-11-03.** The live config now carries the
64-character nonce. The 2026-11-05 secret-exposure audit redacted the
nonce, the master key and the store slug from this file: the repo is
public, the nonce is the input that derives the master key, and the
master key is the derived value itself. Values still exist in git
history until the rotation runs:
[03-nonce-rotation.md](../../docs/reports/2026-11-03-macos-apply-audit/03-nonce-rotation.md).
It derives:

| Value | Derivation | Result |
|---|---|---|
| Master key | `sha256("com.ardju.utils:shellx:" + nonce)` | rendered by `dot_local/share/private_shellx/private_master.key.tmpl`; not published here |
| Store slug | `blake2b(master_key, 16)` | names the store directory |
| Store path | `~/.local/share/<slug>/` | did not exist on 2026-11-03 |

`chezmoi status` now returns 53 targets and the master key renders.

The new nonce changes the store slug. The repo export file is named
`encrypted_shiraki-yuki_621ef85e973ed2676f8c5de1a89d27e8_...`, and that
slug does not match the new one. The import does not care. `shellx import`
reads the target slug from `_read_slug()`. That function falls back to
the derived slug when no `.sl` file exists, and it names the blobs with
that slug. The
slug in the export file name is informational.

## Blocker 5: the signing keys in the repo are not in the local keyring

The repo `dot_gitconfig` sets `signingkey = 0x330FE76C4FD0F3BC`. The repo
`dot_gnupg/gpg.conf` sets `default-key 9909A0802A11B93F`. Neither is in
the local keyring. The live `~/.gitconfig` uses `0x32A87E6BED04FEC6`, which
is present.

So the apply points git at a key that cannot sign. Git falls back to the
default key, so commits stop being signed with the intended identity.

**Fix before apply.** Import the signing keys from the backup, or change
the repo to the key that this host holds. The key IDs are personal to the
canonical host, so the repo value is probably right and the key is missing
here.

**Owner: the user. Open on 2026-11-03.** Verified after `chezmoi init`:
neither `330FE76C4FD0F3BC` nor `9909A0802A11B93F` is in the keyring. Only
`32A87E6BED04FEC6` is. There is no key backup under `~/.gnupg/` or
`~/.local/state/`, so the backup is elsewhere.

## Blocker 6: the apply widens the mode on `~/.ssh`

**Not a hard blocker.** The apply succeeds and SSH keeps working. OpenSSH
checks the private key files and `authorized_keys`, not the `~/.ssh`
directory mode. A key file must not be readable by group or others, and
`authorized_keys` must not be writable by others. `0755` on the directory
is neither.

The apply changes no key file mode on this host. The 15 `~/.ssh/keys/*`
files stay encrypted and skipped, the live key files stay `0600`, and
`authorized_keys` stays `0600`.

It is still a regression worth fixing, because the mode stays wide after
the apply. `~/Library` going `0700` to `0755` is the most exposed of the
three, since it opens the whole tree of app data.

`~/.ssh` goes from `0700` to `0755`, and `~/.ssh/config.d` from `0700` to
`0755`. The repo source dir is `dot_ssh`, which carries no `private_`
attribute.

Verified chezmoi behaviour, with a scratch source tree:

| Source | Target mode |
|---|---|
| `dot_ssh` | `0755` |
| `private_dot_ssh` | `0700` |
| `private_dot_ssh/private_config.d` | `0700` |
| `dot_config/private_cortexkit` | `0700` |

`private_` applies to one path component only. It does not propagate to
nested directories. Each directory that must end up `0700` needs its own
`private_` prefix on that component.

**Fix before apply.** Rename the source dirs:

| Current | New |
|---|---|
| `dot_ssh` | `private_dot_ssh` |
| `dot_ssh/config.d` | `private_dot_ssh/private_config.d` |
| `dot_ssh/keys` | `private_dot_ssh/private_keys` |
| `dot_config/cortexkit` | `dot_config/private_cortexkit` |

`~/Library` also goes `0700` to `0755`. The repo source is `Library`, so
it becomes `private_Library`. Its child `LaunchAgents` stays `0755`, which
matches the live mode. The `Library` change is the more serious of the
three: it opens the whole `~/Library` tree, which holds app data and
`Application Support`.

**Decision on 2026-11-03: apply as-is.** The renames were skipped. The
three directories end up at `0755` and stay that way. The wide modes are
the price for not changing the source layout. If they are fixed later,
rename the source dirs and re-apply.

## The defects the apply exposed are fixed

The PATH collapse, the missing `brew shellenv`, and the wrong target path
in `check_decrypt.sh` are all fixed. The details are in
[`macos-apply-fixed.md`](macos-apply-fixed.md).

## No SSH key reaches this host

The 9 `~/.ssh/config.d/*.conf` files and the 15 `~/.ssh/keys/*` files stay
encrypted and skipped. The host has no age identity, and it must not get
one: those files are the personal machine's SSH keys. The
`check_decrypt.sh` mechanism is what keeps them off this host.
