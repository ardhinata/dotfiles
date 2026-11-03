# macOS apply caveats

The changes an apply brings to the macOS work laptop that do not block it.
Each one either narrows a permission, changes a behaviour, or downgrades a
file.

Companion to [`macos-apply-blockers.md`](macos-apply-blockers.md), which
holds the six blockers, and
[`macos-apply-target-state.md`](macos-apply-target-state.md), which holds
the 53 changed targets.

All findings were verified on 2026-11-03 with chezmoi v2.74.0 against the
live host.

## The cc-safety-net policy gets tighter, not looser

The repo policy removes the `rm.recursive-force-outside-cwd` override and
the secret-extension overrides. Removing an override that says `off` turns
the rule **on**. The live policy has those protections disabled.

The repo `opencode.jsonc` also drops four `rm` deny patterns
(`rm -*rf ./*`, `rm -*rf ../*`, `rm -*fr ./*`, `rm -*fr ../*`) and keeps
only the root and home cases. The comment in the file says the rest is
left to cc-safety-net and to the personal `destructive-actions.md` rule.

So after the apply, `rm -rf` inside the working directory is not blocked
by the OpenCode permission layer any more. The personal rule still asks
for approval. This is a deliberate design choice in the repo, not a
mistake, but it is a real reduction in the guard.

The `ensemble-teams.md` rule file is deleted, because the repo
`opencode.jsonc` drops the ensemble plugin. That is consistent. The live
`~/.config/opencode/ensemble.db` stays on disk as an orphan.

## The AFT index rebuilds

`dot_config/cortexkit/aft.jsonc` changes the identity salt and the vector
width. The 688 MB index in `~/.local/share/cortexkit` rebuilds. That is
expected and not a blocker, but it takes time and it needs the OpenRouter
key from blocker 3.

## `~/.gitconfig` points at a missing include file

The repo `dot_gitconfig` has:

```
[includeIf "gitdir:/Users/muhamad.ardhinata/Work/"]
	path = /Users/muhamad.ardhinata/Work/.gitconfig
```

That file does not exist. Git tolerates a missing include target: it
falls back to the value above it, with no error. Verified. The live
`~/.gitconfig` instead includes `~/Work/local/.git_local`, which does
exist and sets the personal identity.

So after the apply, repositories under `~/Work` lose the per-directory
identity override.

## `~/.p10k.zsh` and `~/.config/tmux/tmux.conf` are downgrades

Both live files are newer than the repo versions. The prompt moves back to
the 2026-05-24 wizard output. The tmux config adds `extkeys` back to
`terminal-features` and restores the shared Wayland wording. The clipboard
bridge still renders `pbcopy` on darwin. Neither breaks the host. Both are
listed in
[`macos-apply-target-state.md`](macos-apply-target-state.md).

## `~/.local/share` goes to mode 0700

The chezmoi script `.chezmoiscripts/run_onchange_init-shellx-store.sh` runs
`chmod 700 "${HOME}/.local/share"`. The directory is `0755` today. The
change is not in the chezmoi diff, because chezmoi does not manage that
path. It only affects the owner, since everything under it belongs to the
user.

## The `~/.config/opencode` and `~/.gnupg` modes

| Path | Change | Note |
|---|---|---|
| `~/.config/opencode` | `0777` to `0755` | An improvement. The live dir is world-writable. |
| `~/.config/opencode/opencode.jsonc` | `0600` to `0644` | The file holds no secret. It names the API key source. |
| `~/.config/cortexkit/magic-context.jsonc` | `0600` to `0644` | The file holds no secret. |
| `~/.gnupg/common.conf` | `0640` to `0644` | The `private_` prefix is on the directory, not the file. |
| `~/.gnupg/gpg-agent.conf` | `0644` to `0600` | The repo file is `private_gpg-agent.conf.tmpl`. |

## The gpg agent starts serving SSH

The repo `private_gpg-agent.conf.tmpl` adds `enable-ssh-support` and the
SSH cache TTLs. The live `~/.gnupg/gpg-agent.conf` has neither, so the
agent does not serve SSH today.

The agent currently holds no identities, so the change is inert on this
host. It matters when keys are loaded. Note that the repo `dot_zshrc`
points `SSH_AUTH_SOCK` at the gpg-agent socket, so the shell is already
prepared for it.
