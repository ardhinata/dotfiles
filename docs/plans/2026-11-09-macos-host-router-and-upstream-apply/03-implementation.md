# Implementation steps

The phases that apply the design in [02-design.md](02-design.md) to the
macOS work laptop. Part of the plan to correct the dotfiles for that host.
See [README.md](README.md) for the index.

## Phase 1: the router and the dispatchers

1. Add `.chezmoitemplates/hosts.yaml` with the `IKM202300278` profile and a
   `_default` profile.
2. Add `.chezmoitemplates/host.yaml.tmpl` with the resolver.
3. Add the `~/.shell/.zshenv` line to `dot_zshenv`.
4. Move the Kiro CLI line and the FastPath block from the live `~/.bashrc`
   to the live `~/.shell/bashrc.local`. Add the dispatcher line to
   `dot_bashrc`.
5. Run `chezmoi diff` and check the change list.

## Phase 2: the PATH fix

1. Rewrite `dot_shell/env/path.sh` with the `_path_front` loop, the
   Homebrew prefix handling, and the helper at the front.
2. Add the second `path.sh` source to `dot_zprofile`.
3. Test the file under `sh`, `bash` and `zsh` in a sandbox home, with a
   controlled PATH.
4. Measure the PATH in four shell types: interactive login, interactive
   non-login, non-interactive login and non-interactive.

## Phase 3: the config files

1. Rename `dot_config/opencode/private_cli.json` to `private_cli.json.tmpl`
   and add the router condition.
2. Add the `environment.d` rule to `.chezmoiignore`, gated on the OS.
3. Take the three safe upstream config changes as they are.

## Phase 4: apply and verify

1. Save a copy of the live targets with `.shell_helper/backup_targets.sh`.
2. Run `chezmoi diff` and read the whole output before any write.
3. Apply with `chezmoi apply --dry-run` first, then `chezmoi apply`.
4. Run the verification list below.

## Risks and mitigations

- Risk: the apply replaces the `~/.zshenv` symlink with a regular file.
  Mitigation: the dispatcher sources the token file. Check the token values
  in a clean environment after the apply.
- Risk: the `~/.zshenv.zwc` bytecode file is stale and shadows the new
  source. Mitigation: the new source file is newer than the bytecode file.
- Risk: the PATH order regresses in one of the four shell types.
  Mitigation: measure all four types after the apply.
- Risk: the hostname changes, so the router falls back to `_default`.
  Mitigation: the fallback prints a warning.
- Risk: the Linux host regresses. Mitigation: every change depends on the
  OS or on the hostname, and the Linux branch renders the upstream files
  unchanged.

## Verification

Run each check after the apply.

```sh
chezmoi diff                                   # only cli.json, as before
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
- Should the router key be the hostname alone, or the hostname and the OS?
  The hostname alone is enough today.
- Should `~/.bashrc` keep the FastPath block? The block does nothing on
  this host, because `~/.fastpath/env` does not exist.

## Decisions

- 2026-11-09: Use a hostname router, not an OS-only switch. The user asked
  for the router, and the remaining differences are per-machine.
- 2026-11-09: Use presence-based dispatch for the secret file. The router
  would need the hostname for a fact that the file system already holds.

## Deferred notes

- The `~/.zshenv.zwc` path was not tested end to end. The host has no
  `zsh/zcompile` module, so the bytecode update step was not reproduced.
- The `python3` version in a non-interactive `zsh -lc` is 3.9.6 today. The
  PATH fix corrects the order, and the fix was not run against the live
  home.
