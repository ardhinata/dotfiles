# Implementation steps

The phases that apply the design in [02-design.md](02-design.md) to the
macOS work laptop. Part of the plan to correct the dotfiles for that host.
See [README.md](README.md) for the index.

Every phase ran on 2026-11-10. The measurements are in
[05-verification.md](05-verification.md).

## Phase 1: the router and the dispatchers

1. Add `.chezmoitemplates/hosts.yaml` with the `IKM202300278` profile and a
   `_default` profile. Done.
2. Add `.chezmoitemplates/host.yaml.tmpl` with the resolver. Done.
3. Add the `~/.shell/.zshenv` line to `dot_zshenv`. Done.
4. Move the Kiro CLI line and the FastPath block from the live `~/.bashrc`
   to the live `~/.shell/bashrc.local`. Add the dispatcher line to
   `dot_bashrc`. Done. The live file was copied as it was, so both blocks
   survived.
5. Run `chezmoi diff` and check the change list. Done.

## Phase 2: the PATH fix

1. Rewrite `dot_shell/env/path.sh` with the `_path_front` loop, the
   Homebrew prefix handling, and the helper at the front. Done.
2. Add the second `path.sh` source to `dot_zprofile`. Done.
3. Test the file under `sh`, `bash` and `zsh` in a sandbox home, with a
   controlled PATH. Done.
4. Measure the PATH in four shell types: interactive login, interactive
   non-login, non-interactive login and non-interactive. Done.

## Phase 3: the config files

1. Rename `dot_config/opencode/private_cli.json` to `private_cli.json.tmpl`
   and add the router condition. Done.
2. Add the `environment.d` rule to `.chezmoiignore`. The rule ignores
   `.config/environment.d` when `.chezmoi.os` is `darwin`, and the
   directory is deployed on Linux. Done.
3. Take the three safe upstream config changes as they are. Done.

## Phase 4: the install without `chezmoi apply`

`chezmoi apply` is banned in this repository. The install writes the
target files from `chezmoi cat`, one file at a time.

1. Save a copy of the live targets with `.shell_helper/backup_targets.sh`.
   The token file is not a chezmoi target, so it is added with
   `--extra .shell/.zshenv`. Done. The backup is at
   `~/.local/state/chezmoi-backup-2026-11-10-macos-router`.
2. Run `chezmoi diff` and read the whole output before any write. Done.
3. Write each target file from `chezmoi cat`. The write goes to a
   temporary file in the same directory, and the temporary file is renamed
   over the target. The rename replaces a symlink instead of following
   it, so `~/.zshenv` loses its link without the token file being
   truncated:

   ```sh
   stage=$(mktemp "$HOME/.zshenv.XXXXXX")
   chezmoi cat "$HOME/.zshenv" > "$stage"
   chmod 644 "$stage"
   mv "$stage" "$HOME/.zshenv"
   ```

   A redirect straight into the target would follow the link and truncate
   `~/.shell/.zshenv`, the only copy of the Jira and Bitbucket tokens.
   Done. The `~/.bashrc` write ran after `~/.shell/bashrc.local` was
   created, so the Kiro line and the FastPath block were in place first.
4. Run the verification list below. Done.

After a by-hand write, `chezmoi status` can still show `M` in the first
column. That column compares the live file with the last state written by
chezmoi, and only an apply updates that state. `chezmoi diff` is the proof
that the target state is reached: it compares the live file with the target
state.

## Risks and mitigations

- Risk: the install replaces the `~/.zshenv` symlink with a regular file.
  Mitigation: the dispatcher sources the token file. The token values are
  checked in a clean environment after the install.
- Risk: the `~/.zshenv.zwc` bytecode file is stale and shadows the new
  source. Mitigation: the new source file is newer than the bytecode file.
- Risk: the PATH order regresses in one of the four shell types.
  Mitigation: measure all four types after the install.
- Risk: the hostname changes, so the router falls back to `_default`.
  Mitigation: the fallback prints a warning.
- Risk: the Linux host regresses. Mitigation: every change depends on
  the OS or on the hostname, and the Linux branch renders the upstream
  files unchanged.

## Verification

Run each check after the install.

```sh
chezmoi diff                                   # empty
env -i HOME="$HOME" /bin/zsh -c 'echo "${JIRA_API_TOKEN:+SET}"'
env -i HOME="$HOME" /bin/zsh -c 'command -v shellx'
env -i HOME="$HOME" /bin/zsh -c 'shellx list'
env -i HOME="$HOME" PATH=/usr/bin:/bin TERM=dumb /bin/zsh -lc 'command -v python3'
opencode debug config
```

## Open questions

- Should the tokens move into the shellx store, and the token file at
  `~/.shell/.zshenv` go away? The store holds one value today. The file
  has mode 0644, and the compiled `~/.zshenv.zwc` holds a second copy.
  The dispatcher keeps the file in place, so the answer can wait.
- Should the router key be the hostname alone, or the hostname and the OS?
  The hostname alone is enough today.
- Should `~/.bashrc` keep the FastPath block? The block does nothing on
  this host, because `~/.fastpath/env` does not exist.

## Decisions

- 2026-11-09: Use a hostname router, not an OS-only switch. The user asked
  for the router, and the remaining differences are per-machine.
- 2026-11-09: Use presence-based dispatch for the secret file. The router
  would need the hostname for a fact that the file system already holds.
- 2026-11-10: Keep the hostname as the router key. The hostname is an
  asset tag, not a credential. It grants no access on its own, and it is
  already in the tracked plan files of this repository.
- 2026-11-10: The router and `system_environment.profile` stay separate.
  The profile selects the section of the shellx secret store, and the
  router selects the content the repo renders.

## Deferred notes

- None. The `~/.zshenv.zwc` question is closed: the compiled bytecode is
  older than the new source file, and the non-interactive shell resolves
  the PATH from the new source, so the bytecode does not shadow it. The
  `zsh/zcompile` module does not load on this host because `zcompile` is a
  builtin in zsh 5.9, and the builtin works.
