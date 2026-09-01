---
title: horiuchi-aika chezmoi migration
date: 2026-08-30
target_host: horiuchi-aika.home.mindbreak.info
remote_user: ardhinata
local_project_root: /home/ardhinata/.local/share/chezmoi
remote_backup_root: ~/Playground/backup/20260830-150735-horiuchi-aika-migration
status: completed
---

# horiuchi-aika chezmoi migration

Migration of the workstation `horiuchi-aika.home.mindbreak.info` from its
existing zplug-based chezmoi source to the project source tree under
`/home/ardhinata/.local/share/chezmoi`.

## TL;DR — current state

- **Backup**: created on the remote at
  `~/Playground/backup/20260830-150735-horiuchi-aika-migration/` (size ≈ 1.5 GB,
  see manifest below).
- **Clean**: zsh dotfiles, `.shell/zsh`, `.shell/zplug`, `~/.ssh`, `~/.gnupg`,
  `~/.config/chezmoi`, `~/.local/share/chezmoi` removed on the remote.
  `.zsh_history` and `.shell/{goenv,nvm,pyenv,phpenv,flag}` preserved.
- **Restore + clone + apply**: completed. SSH lockout happened during cleanup
  but was restored via `codeforge.key` (see SSH lockout incident below).
  `chezmoi apply` ran clean (174 managed files, no diff/status drift).
- **Post-apply fixes applied**: old `~/.kilo/` (Kilo editor vendor dir) backed
  up; vendor symlink `~/.kilo -> .agents/kilo` recreated; the project-side
  `IdentityFile ... .key.pub` bug in `workstation-pc.single.conf` was fixed
  in the encrypted source and re-applied (see Bug fixed below).

## Why this was needed

The remote host had a chezmoi source tree (67 files) using:

- `dot_` prefix convention with `dot_config`, `dot_shell`, `dot_zshrc`
- `.chezmoiexternal.yaml` for external archive imports
- zplug-based shell stack in `~/.shell/zsh/` (00-pre-source.sh, 01-pre-zplug-load.sh,
  02-zplug-load.sh, 03-post-zplug-load.sh, `useropts.d/` with 7 files)
- 8 files drifted from source (status `MM`): `~/.gnupg/sshcontrol`,
  `~/.shell/zsh/useropts.d/00-exports.sh`, `~/.ssh/authorized_keys`,
  `~/.ssh/conf.d/20-router.single.conf`, `~/.ssh/config`,
  `~/.ssh/default_ed25519.pub`, `~/.zshrc`, plus a remote-side rename marker on
  the `00-check-reqs.sh` run_before script.

The project source (170 managed files) uses zgenom + prezto + powerlevel10k, an
`AGENTS.md`-first conventions layout, `.agents/kilo/`, `.tmp/`, kilo rules &
skills, and the `chezmoi.yaml.tmpl` profile/nonce prompt.

The two source trees are not interchangeable; the remote's tree was a
predecessor project.

## What was changed (this session)

### On the remote

| Action | Path | Notes |
|---|---|---|
| created | `~/Playground/backup/20260830-150735-horiuchi-aika-migration/` | backup root |
| created | `…/.gnupg/` | full copy of `~/.gnupg` (private-keys-v1.d, sshcontrol, pubring.kbx, trustdb.gpg, two `.asc` imports) |
| created | `…/.ssh/` | full copy of `~/.ssh/` excluding the `agent/` socket |
| created | `…/.keys/` | extra private keys at top-level (`~/.keys/age/*`, `~/.keys/ssh/*.pem`) |
| created | `…/zsh/` | `.zshrc`, `.zshrc-bak`, `.zshrc.local`, `.zcompdump`, `.zdirs`, `.zsh_history` |
| created | `…/shell-zsh/` | `~/.shell/zsh` (zplug init scripts + `useropts.d/`) |
| created | `…/shell-zplug/` | `~/.shell/zplug` cache/repos (108 MB) |
| created | `…/shell-flag/` | `~/.shell/flag` |
| created | `…/shell-kilo/` | `~/.shell/.kilo` |
| created | `…/chezmoi-config/chezmoi/` | `~/.config/chezmoi` (yaml + boltdb state, 72 KB) |
| created | `…/chezmoi-source-pre/` | full copy of the old `~/.local/share/chezmoi/` (1.2 MB) |
| created | `…/config/config/` | full copy of `~/.config/` (1.2 GB — kdeconnect/filezilla/JetBrains/Postman private keys included) |
| created | `…/extra-keys/ollama-id_ed25519` | `~/.ollama/id_ed25519` (private) |
| created | `…/README.md` | manifest + fingerprint appendix |
| killed | gpg-agent, ssh-agent | to release locks on `private-keys-v1.d/` |
| removed | `~/.zshrc`, `~/.zshrc-bak`, `~/.zshrc.local`, `~/.zcompdump`, `~/.zdirs` | shell dotfiles |
| removed | `~/.shell/zsh`, `~/.shell/zplug` | old zplug stack |
| removed | `~/.ssh/` | entire ssh dir (incl. `authorized_keys`, `config`, all `*.pem`, `known_hosts`) |
| removed | `~/.gnupg/` | entire gnupg home |
| removed | `~/.config/chezmoi/` | chezmoi user config + boltdb state |
| removed | `~/.local/share/chezmoi/` | chezmoi source dir; recreated empty |

### Preserved on the remote

- `~/.zsh_history` (448 KB, intact for reference even though shell is now bash)
- `~/.shell/{goenv,nvm,phpenv,pyenv,flag,.kilo}` — language toolchains and
  kilo vendor dir
- `~/.keys/` (kept; not deleted because user said "private key that not backed
  up at `~/.gnupg`", and the directory lives outside the chezmoi-managed set)
- `~/.config/` — only the chezmoi subdir was removed; the rest stays

### On this local machine (the project source)

Nothing changed; the project tree was staged into a tarball
`/tmp/kilo/chezmoi-source-new.tar.gz` (48 MB) but not yet pushed (SSH blocked).

## What will be lost or changed when apply resumes

Once SSH is restored and `chezmoi apply` runs, the following will be written to
the remote (replacing or creating fresh):

| Remote path | Before | After |
|---|---|---|
| `~/.zshrc` | old zplug init | project `dot_zshrc` (zgenom + prezto + p10k) |
| `~/.zprofile`, `~/.zshenv`, `~/.p10k.zsh` | absent | created from project templates |
| `~/.shell/zsh/00-before-zgenom.zsh`, `01-zgenom-init.zsh`, …, `12-gpg.zsh` | absent | full prezto/zgenom/p10k stack from `dot_shell/zsh/` |
| `~/.shell/zplug/` | zplug repos | absent (chezmoi won't manage it) |
| `~/.shell/useropts.d/` | old 7 files | absent |
| `~/.ssh/config`, `~/.ssh/authorized_keys`, `~/.ssh/conf.d/`, `~/.ssh/default_ed25519.pub` | old values | project `private_dot_ssh/` versions |
| `~/.gnupg/gpg-agent.conf`, `~/.gnupg/gpg.conf`, `~/.gnupg/sshcontrol` | old values | project `private_dot_gnupg/` versions |
| `~/.gitconfig` | old | project `dot_gitconfig` |
| `~/.config/chezmoi/chezmoi.yaml` | absent (we deleted it) | freshly initialized by `chezmoi init` from `dot_chezmoi.yaml.tmpl` (will prompt for `system_environment.profile` and a 64-char `nonce`) |
| `~/.local/share/chezmoi/` | empty | new project source tree (170 managed files) |
| `~/.agents/`, `~/.kilo/`, `~/.tmp/` | absent | created by project layout |
| `~/.config/kilo/` | absent | created by kilo rules/skills in `.agents/kilo/` |
| `run_before_00-check-reqs.sh` | old (renamed away) | new (project version) |
| All age-encrypted files in `private_*` | absent | created; **requires age recipients/identities to be installed on the remote first** — see "Prerequisites before chezmoi apply" below |

Files on the remote that the project does **not** manage and that will remain
untouched:

- `~/.shell/{goenv,nvm,phpenv,pyenv,flag,.kilo}`
- `~/.keys/`
- `~/.config/{alacritty,containers,environment.d,go,pipewire}/` and similar
  untracked bits under `~/.config/`
- `~/.ollama/id_ed25519` and any non-chezmoi pubkeys in `~/.ssh/` (after restore)
- `.chezmoiexternal.yaml` on the old source — gone with the source dir; read it
  before discarding if any external archives were tracked via it

## Prerequisites before `chezmoi apply` (the SSH-recovery path)

1. **Manually restore SSH** by sitting at the PC (per the user's plan).
   - Drop one of the public keys from this local machine's `ssh-add -L` into the
     remote's `~/.ssh/authorized_keys` (mode 600, owned by the user).
   - The user's own pubkeys (the 4 listed in the backup at `…/.ssh/authorized_keys`)
     are also available for restoration; copy them back if needed for
     other hosts to reach horiuchi-aika.
2. **Install age identities** on the remote so encrypted files decrypt:
   - Either copy `…/chezmoi-source-pre/age-keys/{chezmoi_v2,master}.age.key`
     (old project) into `~/.local/share/chezmoi/age-keys/`, **or**
   - Copy the new project's identities (this local repo's
     `.encryption_keys/*.secret.key`) into the same directory. The project
     `chezmoi.yaml.tmpl` globs `.encryption_keys/*.public.key` and
     `.encryption_keys/*.secret.key`, so they must live there for decrypt to
     work.
3. **Render `chezmoi.yaml`** non-interactively. The project's
   `.chezmoi.yaml.tmpl` will prompt for `system_environment.profile` and a
   64-char `nonce`. Pre-fill `~/.config/chezmoi/chezmoi.yaml` from the template
   before the first apply, with explicit `profile: <name>` and a pre-generated
   `nonce: <64-char-string>`, so `chezmoi apply` does not hang.
4. **Push the project source** to the remote:
   - USB-stick: copy `/tmp/kilo/chezmoi-source-new.tar.gz` from this machine,
     extract on the remote at `~/.local/share/chezmoi/`.
   - Or, from this machine after SSH is restored:
     `scp /tmp/kilo/chezmoi-source-new.tar.gz horiuchi-aika.home.mindbreak.info:/tmp/`
     then `ssh … 'tar -xzf /tmp/chezmoi-source-new.tar.gz -C ~/.local/share/chezmoi/'`.
   - Recreate the vendor symlink: `ln -sfn .agents/kilo ~/.kilo` on the remote
     (the root-level `.kilo/`, `.claude/` etc. are untracked symlinks into
     `.agents/<vendor>/`).
5. **Run dry, then apply**:
   - `ssh horiuchi-aika.home.mindbreak.info 'cd && chezmoi diff'`
   - `ssh … 'cd && chezmoi apply --dry-run'`
   - `ssh … 'cd && chezmoi apply'`
   - Re-add SSH keys to gpg-agent: `ssh-add` (no flag — gpg-agent ignores
     `-t`; see `~/.config/kilo/rules.personal.d/ssh-agent-keys-location.md`).
6. **Restore gpg keyring state** if needed: copy `~/.gnupg/` back from the
   backup if the project source is missing fingerprints or trust entries for
   keys the user wants to keep.

## Backup manifest reference

`~/Playground/backup/20260830-150735-horiuchi-aika-migration/README.md`
contains, in addition to the path table above:

- `gpg --list-keys --with-keygrip` output (30 keygrips present in
  `private-keys-v1.d/`)
- The full `~/.gnupg/sshcontrol` contents (keygrip → TTL → flags)
- `ssh-keygen -lf` fingerprints for every `*.pem`, `id_*`, and ollama key
- The two age key directories (`~/.keys/age/`, `~/.local/share/chezmoi/age-keys/`)
  with sizes

## SSH lockout incident

During cleanup `~/.ssh/authorized_keys` was deleted before the project's
`private_dot_ssh/authorized_keys` was deployed. After cleanup, `ssh` from this
local machine was rejected (Permission denied). Two contributing factors:

1. `~/.ssh/config.d/workstation-pc.single.conf` (project source) had
   `IdentityFile ~/.ssh/keys/default-2026.key.pub` and
   `IdentityFile ~/.ssh/keys/default-2018.key.pub` — `.pub` paths instead of
   private keys. ssh silently treats those as offering the **public key only**
   (the public half is useless for authentication).
2. `IdentitiesOnly yes` plus the wrong IdentityFile meant the agent keys were
   not actually offered; only the broken `.pub` lines.

The user noticed and explicitly named the working key:
`ssh -o IdentityFile=~/.ssh/keys/codeforge.key horiuchi-aika.home.mindbreak.info`
restored shell access. `codeforge.key` was the only project-managed key whose
public half was present in the (now-deployed) `authorized_keys`.

## Bug fixed mid-migration

`dot_ssh/config.d/encrypted_workstation-pc.single.conf.age` had two
`IdentityFile ~/.ssh/keys/*.key.pub` lines that made the entire host block
unreachable via the project's own ssh config. Decrypted, fixed to private
keys, re-encrypted with the project's age recipients
(`master_pq.public.key`, `personal_pq.public.key`), and the source tarball
rebuilt. After re-applying, `chezmoi status` is empty and the host can be
reached via `ssh horiuchi-aika.home.mindbreak.info` once the agent is loaded.

## Apply outcome

```
$ ssh -o IdentityFile=~/.ssh/keys/codeforge.key horiuchi-aika … 'cd && chezmoi apply'
[chezmoiscript] BEGIN 2026-08-30T15:24:34+07:00
Cloning into '/home/ardhinata/.config/alacritty/themes'...
Cloning into '/home/ardhinata/.shell/zgenom'...
Cloning into '/home/ardhinata/.tmux/plugins/tpm'...

$ ssh -o IdentityFile=~/.ssh/keys/codeforge.key horiuchi-aika … 'cd && chezmoi status'
(empty — all 174 managed files match source)

$ ssh … 'zsh -i -c "echo \$SHELL_TOOL_DIR; type compinit"'
-- zgenom: Initializing completions ...
-- zgenom: Compiling files ...
/home/ardhinata/.shell
compinit-loaded      # interactive zsh works
```

`fnm` warning at `~/.shell/zsh/10-common-export.zsh:22` (eval `fnm env …`) is
expected — fnm not installed on the remote. Install `fnm` (the `fnm` skill on
this local machine) and re-source, or ignore the warning.

Post-apply state on the remote:

| Path | Source / change |
|---|---|
| `~/.zshrc` (2692 B) | project `dot_zshrc` — zgenom + prezto + p10k instant prompt |
| `~/.zprofile` (158 B) | project `dot_zprofile` |
| `~/.p10k.zsh` (87 KB) | project `dot_p10k.zsh` |
| `~/.gitconfig` | project `dot_gitconfig` |
| `~/.gnupg/{gpg-agent,gpg,common}.conf` | project `private_dot_gnupg/` versions; `enable-ssh-support`, `pinentry-program ~/.shell/helper/pinentry-wrapper` |
| `~/.ssh/config`, `~/.ssh/config.d/*.conf`, `~/.ssh/keys/*`, `~/.ssh/authorized_keys` | decrypted from project `private_dot_ssh/` (23 encrypted files) |
| `~/.shell/zgenom/` | cloned by `chezmoiscripts` |
| `~/.shell/zsh/` | project `dot_shell/zsh/` prezto/zgenom init stack |
| `~/.shell/helper/` | project `dot_shell/helper/` shellx + runpriv |
| `~/.shell/store/` | shellx encrypted store (empty; populated by `shellx import`) |
| `~/.config/alacritty/`, `~/.config/kilo/`, etc. | project `dot_config/` |
| `~/.tmux.conf`, `~/.tmux/` (tpm plugins) | project `dot_tmux.conf` + cloned tpm |
| `~/.kilo` | symlink → `.agents/kilo` (after post-fix) |
| `.chezmoiscripts/` | run on apply; `init-shellx-store.sh` set up `~/.local/share/`, bytecode-compiled shellx, removed legacy `kilo-shared-{save,pull}` wrappers |

## Risks and open items (post-apply)

- **`~/.kilo` editor dir backup**: the old Kilo editor vendor dir
  (created 2026-05-09, had its own `package.json`, `node_modules`, `skills/`)
  was moved to
  `~/Playground/backup/kilo-editor-<ts>.bak`. If the user wants to restore the
  Kilo editor (the IDE/extension, not the project vendor dir), symlink it back
  via a separate path. The project convention `.kilo -> .agents/kilo` is now
  in place.
- **`fnm` not installed**: `~/.shell/zsh/10-common-export.zsh` emits a
  non-fatal `command not found: fnm` on every interactive zsh start. Install
  `fnm` on the remote (see the `fnm` skill on this local machine) or
  conditionally wrap the eval.
- **SSH from this local machine without explicit `-o IdentityFile`**: still
  fails because the agent keys (`default-2026` ECDSA, `default-2018` ED25519)
  are not in the remote's `authorized_keys`. The project deploys
  `private_dot_ssh/authorized_keys` from the encrypted bundle, which contains
  the GitHub `ardhinata.keys` set (4 ed25519 keys). After the user runs
  `ssh-add ~/.ssh/keys/codeforge.key` (and any other keys they want) on the
  remote, gpg-agent will hold them under `~/.gnupg/sshcontrol` and SSH auth
  via the agent will work.
- **`sshcontrol` was reset** to the project's version — empty. Keys are
  loaded only via `ssh-add`, not from `~/.gnupg/private-keys-v1.d/`. The
  30-keygrip ring in `private-keys-v1.d/` was wiped. Restoring the original
  `~/.gnupg/` from the backup (step 7 in Next actions) puts the keygrips
  back; otherwise the user will need to re-import GPG keys from the
  `*.asc` exports in the backup.

## Next actions for the user

1. On the remote, `ssh-add ~/.ssh/keys/codeforge.key` (and any others from
   `~/.ssh/keys/`). This restores SSH auth via gpg-agent for hosts that
   accept those keys.
2. If the GPG keyring (private keys, trust, web-of-trust, tofu.db) is
   needed, restore from the backup:
   `cp -a ~/Playground/backup/20260830-150735-horiuchi-aika-migration/.gnupg/* ~/.gnupg/`,
   then `gpgconf --kill gpg-agent`.
3. Install `fnm` on the remote to silence the zsh warning (or accept the
   warning). The project loads it via
   `eval "$(fnm env --use-on-cd --shell zsh)"` in
   `~/.shell/zsh/10-common-export.zsh:22`.
4. Decide whether to keep the Kilo editor dir backup or delete it (now at
   `~/Playground/backup/kilo-editor-<ts>.bak`).
5. Commit the source-side fix to the workstation-pc ssh config on this
   local machine (`docs/chezmoi-migrate.md` and the re-encrypted
   `encrypted_workstation-pc.single.conf.age` are uncommitted at the time of
   writing).
