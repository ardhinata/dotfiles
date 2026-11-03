# The macOS work laptop could not run chezmoi apply

What `chezmoi apply` does on the macOS work laptop, the six blockers it
found, and the tooling that makes the apply reversible.

**Status: open.** Blockers 2, 3 and 5 remain with the owner. The apply
itself has not run.

## Index

| File | Contents |
|---|---|
| [01-blockers.md](01-blockers.md) | The six blockers, what was done about each, and what remains |
| [02-tooling.md](02-tooling.md) | The `check_decrypt.sh` path-mapping bug, the rewrite, and the new backup tool |

## Summary

The dotfiles source tree assumed one Linux host. Commit `f855bab` made
the shared files portable. It landed on 2026-11-03, and the macOS work
laptop had not run an apply with it.

The audit found six blockers. Each one changes what the apply does:

- Two embeddings proxy agents would fight for port 8099.
- The shell would lose SDKMAN and OpenBLAS.
- The OpenRouter key would go unset, because the shellx store does not
  exist on this host.
- The apply would stop before it started, because the live chezmoi config
  predates the nonce that the master key template needs.
- Git would sign with a key that is not in the local keyring.
- The mode on `~/.ssh`, `~/.config/cortexkit` and `~/Library` would widen.

The audit resolved blocker 1. It stopped and deleted the live launchd
agent, so the repo agent is the only one. The owner ran `chezmoi init`,
so the nonce is in place. The signing keys still need a restore.

The audit also produced two pieces of tooling. The `check_decrypt.sh`
helper had a path-mapping bug that would make the apply die on an
encrypted file. The audit rewrote it and added a regression test. A new
`backup_targets.sh` copies the live targets that an apply changes, so the
apply can be undone.

## Environment

| Part | Value |
|---|---|
| Host | macOS 26.7.1, arm64, `IKM202300278` |
| chezmoi | v2.74.0, commit `fcc38cf6fdb3a79ae4afae9ef6ad241890db6cde`, Homebrew |
| Source directory | `~/.local/share/chezmoi` |
| Live config | `~/.config/chezmoi/chezmoi.yaml` |
| Python | Homebrew 3.15.2; system `/usr/bin/python3` is 3.9.6 |
| Shell | zsh with zgenom, prezto and powerlevel10k |
| Changed targets | 53, in 54 diff entries |

The 53 and the 54 differ because `~/.zshrc` and `~/.zprofile` each appear
twice: once as a deleted symlink and once as a new file.

## Steps to reproduce

1. Start from the live config of 2026-11-03, before `chezmoi init` ran.
2. Run `chezmoi status` on the macOS host.
3. Observe the empty output and the error text below.
4. Run `chezmoi apply --dry-run --force --verbose` with a config that
   carries the nonce, and read the 53 changed targets.

## Expected

`chezmoi status` lists the targets that differ between the source tree
and the live home directory. `chezmoi apply --dry-run` prints the same
list as a diff, and it does not touch the destination.

## Actual

Before `chezmoi init` ran, every chezmoi command that rendered the
target state failed:

```text
chezmoi: warning: config file template has changed, run chezmoi init to regenerate config file
chezmoi: .local/share/shellx/master.key: template: dot_local/share/private_shellx/private_master.key.tmpl:13:63: executing "dot_local/share/private_shellx/private_master.key.tmpl" at <.system_environment.nonce>: map has no entry for key "nonce"
```

`chezmoi status` printed nothing at all. The failure was not a warning.
It was the whole output.

With the nonce present, the apply rendered. The 53 targets include a
launchd agent with a different label, a new shell setup, a new git
identity, and a new gpg agent config.

## Impact

The apply was one command away from breaking four things on a work
laptop:

- the embeddings proxy
- the shell environment
- the OpenRouter key that the AFT index and the magic context read
- git signing

The launchd blocker was the sharpest. The apply would add a second
proxy agent. That agent would crash-loop in the background on every
apply, and the apply output would show no error at all.

The cost of the audit was one day of investigation on a host that was
otherwise idle. The cost of skipping it was a broken shell.

## Workaround

None is needed now. The blockers are documented, the backup exists, and
the owner has the remaining three.

## Related

- [2026-11-03-macos-apply-breaks-shell-path.md](../../post-mortem/2026-11-03-macos-apply-breaks-shell-path.md)
  — the post-mortem for the broken PATH that the apply deployed
- [2026-11-03-macos-host-portability.md](../2026-11-03-macos-host-portability.md)
  — the source-state change that started this, and the stale instruction
  to copy the personal age identity onto this host
- [.agents/docs/macos-apply-blockers.md](../../../.agents/docs/macos-apply-blockers.md)
  — the agent-facing blocker note, with the full migration gap list
- [.agents/docs/macos-apply-target-state.md](../../../.agents/docs/macos-apply-target-state.md)
  — the agent-facing note for all 53 targets and the decision each one
  needs
- [.agents/docs/macos-apply-caveats.md](../../../.agents/docs/macos-apply-caveats.md)
  — the agent-facing note for the changes that do not block
- [.agents/docs/macos-apply-fixed.md](../../../.agents/docs/macos-apply-fixed.md)
  — the agent-facing note for the defects the apply exposed
- [.agents/docs/macos-host-handoff.md](../../../.agents/docs/macos-host-handoff.md)
  — the brief for an agent that works on the macOS host
- [.shell_helper/README.md](../../../.shell_helper/README.md) — the two
  source-only helper scripts and how to run them
