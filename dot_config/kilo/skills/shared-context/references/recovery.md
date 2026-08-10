# Recovery and Cleanup

## Recovering an abandoned branch

When a worktree is destroyed without merging its shared-context
branch back, the branch is kept (per the locked design). To recover
its commits:

```sh
# List all branches in the shared context bare repo.
git -C ~/.local/share/kilo/shared-context/<slug>.git branch -a

# Inspect the abandoned branch's tip.
git -C ~/.local/share/kilo/shared-context/<slug>.git log --oneline <worktree-slug>

# Cherry-pick the relevant commits into the current worktree's branch.
cd <project>/.tmp/docs
git fetch origin '<worktree-slug>'
git cherry-pick <commit-hash>
kilo-shared-save "recovery: cherry-pick from <worktree-slug>"
```

If the abandoned branch's work overlapped with the current worktree
(rare; surfaces as merge conflicts during cherry-pick), reconcile by
hand.

## Cleaning up stale branches

Branches are kept forever by default. To delete one whose work has
been merged or abandoned:

```sh
git -C ~/.local/share/kilo/shared-context/<slug>.git branch -d <worktree-slug>
```

`-d` refuses to delete unmerged branches. Use `-D` to force-delete
after you've confirmed nothing valuable remains.

## Restoring after a wiped `~/.local/share/`

If the bare repo is lost (machine reset, `~/.local/share/` deletion
without backup), the shared context is irrecoverable. The agent's
unmerged work in `.tmp/docs/` is also gone. This is the primary risk
the locked design accepts in exchange for no-remote simplicity.

Mitigation options (not in scope for the locked design):

- Push the bare repo to a private GitHub/GitLab remote (modifies the
  setup script to add a remote + cron fetch)
- Periodically `tar` `~/.local/share/kilo/shared-context/` to backup
  storage
- Promote important notes/plans/postmortems from `.tmp/docs/` to
  project-tracked docs (`docs/plans/`, `docs/postmortems/`) so they
  live with the project's git history

## Migrating an existing `.tmp/notes/` and `.tmp/plans/`

For projects that pre-date the shared-context design, the migration is:

1. `mkdir -p <project>/.tmp/docs/notes <project>/.tmp/docs/plans <project>/.tmp/docs/postmortems <project>/.tmp/docs/user_cache`
2. `mv <project>/.tmp/notes/* <project>/.tmp/docs/notes/`
3. `mv <project>/.tmp/plans/* <project>/.tmp/docs/plans/`
4. `mv <project>/.tmp/user_cache/* <project>/.tmp/docs/user_cache/` (if any)
5. `rmdir <project>/.tmp/notes <project>/.tmp/plans <project>/.tmp/user_cache` (if empty)
6. Run the setup-script's init sequence (first-worktree bootstrap).
7. Initial commit: `kilo-shared-save "init: migrate from .tmp/{notes,plans,user_cache}/"`

The `.tmp/migration/` dir is unrelated and stays put.

## Re-running the setup script

Safe to re-run. The setup script's first-worktree detection (`is
`$HOME/.local/share/kilo/shared-context/<slug>.git` a bare repo?`) is
idempotent. If the bare repo exists, the init sequence skips the
`git init --bare` and the initial commit. If a clone exists but the
hook is missing, the script re-installs the hook.