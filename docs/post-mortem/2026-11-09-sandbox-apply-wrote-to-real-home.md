---
severity: high
status: resolved
date: 2026-11-09
owner: the dotfiles maintainer
---

# A sandbox `chezmoi apply` wrote to the real home directory — post-mortem

## Summary

While reviewing `origin/main` for the macOS work laptop, the agent ran a
`chezmoi apply` intended to land in a throwaway sandbox. The apply wrote to
the **real** home directory instead.

The sandbox config file used the key `destinationDir`. chezmoi does not
recognise that key. The real key is `destDir`. chezmoi therefore fell back
to its default destination, which is `$HOME`, and applied the `origin/main`
source tree to the real home directory.

Ten paths in `$HOME` changed. Seven files took the `origin/main` content,
one file took a rendering derived from the sandbox nonce, and two files
were new. The most serious loss was `~/.zshenv`, which was a symlink to
the file that holds the Jira and Bitbucket API tokens. The token file
itself was intact. Nothing was deleted, and no secret was exposed.

The host was restored on the same day. The restore used read-only chezmoi
commands and direct writes, without `chezmoi apply`. See the Resolution
section.

This is the second occurrence of the same class of mistake. In the earlier
session the agent ran four sandbox applies with `chezmoi --source ... --
destination ...`; those wrote to the sandbox correctly, but they left four
sandbox paths in the real state database.

## Detection

The agent noticed it itself, two minutes after the apply. The sandbox apply
printed `Already up to date.` three times while the real home changed
underneath it. The agent compared the sandbox home against the real home and
found the real home modified.

The user then stopped the work and asked for this post-mortem.

No alarm, test or log reported the fault. `chezmoi apply` prints nothing
about the destination it chose, and it ignores a config key it does not
know.

The three `Already up to date.` lines are not from chezmoi. They are the
message that `git pull --ff-only` prints, and `origin/main` carries three
`git-repo` externals. One line per external. The message that would have
revealed the fault never appeared, because it is the only line chezmoi
prints when it works as intended.

## Timeline

All times are local time on the work laptop, UTC+0700.

| Time | Event |
|---|---|
| 2026-11-09 12:38 | First session. Four sandbox applies run with `chezmoi --source <dir> --destination <dir>`. Each writes to its own sandbox home, as intended. Each leaves its sandbox path in the real state database. |
| 2026-11-09 12:46 | The real state database is last written by a sandbox apply. |
| 2026-11-09 15:04 | Second session. The agent writes `sandbox-apply.sh`, a script that runs `chezmoi --config <sandbox>/chezmoi.yaml apply`. The sandbox config sets `destinationDir`. chezmoi ignores that key and applies to `$HOME`. |
| 2026-11-09 15:04:23 | `~/.bashrc`, `~/.agents/rules.opencode/web-verification.md` and `~/.config/zed/settings.json` are overwritten. The `~/.config/alacritty/themes` external is pulled. |
| 2026-11-09 15:04:25 | `~/.config/opencode/cli.json`, `~/.config/opencode/opencode.jsonc`, `~/.config/environment.d/10-shell-env.conf`, `~/.shell/env/path.sh` and `~/.local/share/shellx/master.key` are written. `~/.shell/zsh/10-common-export.zsh` is overwritten. The `~/.shell/zgenom` external is pulled. |
| 2026-11-09 15:04:26 | The `~/.tmux/plugins/tpm` external is pulled. |
| 2026-11-09 15:04:27 | `~/.zshenv` is replaced. The symlink to `~/.shell/.zshenv` becomes a regular file. |
| 2026-11-09 15:05 | The agent finds the real home changed and stops. |

## Root cause

### 1. The config key is `destDir`, not `destinationDir`

chezmoi's config file accepts a destination directory under the key
`destDir`. The list of recognised keys is in
`.help/chezmoi-docs/docs/reference/configuration-file/variables.md.yaml`.
`destinationDir` is not in that list.

A config file with an unrecognised key is not an error. chezmoi reads the
keys it knows and ignores the rest. The agent confirmed this with a
read-only probe:

```text
$ chezmoi --config probe/cfg.yaml target-path "$PWD/probe/src/dot_probe"
/Users/muhamad.ardhinata/.probe        # destinationDir: ignored, fell back to $HOME

$ chezmoi --config probe/cfg3.yaml target-path "$PWD/probe/src/dot_probe"
/private/var/.../probe/home/.probe    # destDir: honoured
```

The probe used a throwaway source directory with one file, so the only
effect was a failed path lookup. Nothing was written.

### 2. The script applied before it checked where the apply would land

`sandbox-apply.sh` had no dry-run step and no destination assertion. It
built the sandbox, wrote the config, and ran the apply. The first thing it
did with the result was read the sandbox home.

A safer order was available and was used in the earlier session. The
`--destination` flag cannot be silently ignored, because an unrecognised
flag makes chezmoi exit with an error. The earlier session used
`--source` and `--destination` flags for exactly this reason. The second
session switched to a config file, and lost that property.

### 3. The verification step could not fail

The script built the sandbox home itself: it wrote the fake token file to
`$SB/home/.shell/.zshenv` and created the symlink
`$SB/home/.zshenv -> .shell/.zshenv`. It then applied, and then checked
that same fake home.

So the check inspected a fixture the script had built by hand. The apply
never went there, and the fixture looked exactly as the script had left
it. The check reported a symlink and a visible fake token, and the script
printed a pass.

The check would have printed the same result whether the apply had
succeeded, done nothing, or written to the real home. A check that cannot
distinguish these three outcomes is not a check.

The check should have asked what the real home looked like **before** the
apply, and compared it afterwards.

### 4. chezmoi gives no signal that it ignored a key

The apply printed three `Already up to date.` lines and nothing else. No
warning named the unknown key. `chezmoi` also prints no line naming the
destination it used, even with `--verbose`.

This is the property that made the fault silent. A tool that ignores an
unrecognised key is reasonable. A tool that ignores an unrecognised key
which was meant to redirect a write is dangerous.

## Impact

| Measure | Value |
|---|---|
| Hosts affected | 1, the macOS work laptop |
| Duration | 15:04:23 to the restore at 17:58, about 2 hours 54 minutes |
| Files changed in `$HOME` | 10 paths, plus 2 new directories |
| Files deleted | None |
| Git externals pulled | 3, in `~/.shell/zgenom`, `~/.tmux/plugins/tpm` and `~/.config/alacritty/themes`. No content moved. |
| Secret material exposed | None. The token file was not read and not copied. |
| Token loading broken | Yes, for new shells, from 15:04 to 17:58. `~/.zshenv` no longer sourced `~/.shell/.zshenv`. |
| shellx store readable | No, from 15:04 to 17:58. The master key on disk no longer matched the stored blobs. |
| Repo source tree | Clean. `git status --short` is empty. The `origin/main` worktree is clean. |
| Upstream `origin/main` | Unchanged. The review conclusion stands. |

### The ten changed paths

The "before" column is the state of the live file at 15:04:23. The
pre-incident `chezmoi --source . diff` in the first session listed exactly
one drift, `.config/opencode/cli.json`. Every other managed file therefore
matched the `main` rendering before the apply.

| Path | Before | After | Recoverable |
|---|---|---|---|
| `~/.zshenv` | symlink to `~/.shell/.zshenv` | regular file with the `origin/main` content | Yes. Restore the symlink. The token file is byte-identical to the backup. |
| `~/.bashrc` | Kiro CLI PATH block and the fastpath block | `origin/main` version | Yes. The prior content is preserved in the tool output of the session that read it. |
| `~/.config/opencode/cli.json` | had `session.image_preview`, `session.sidebar`, `session.markdown`, `session.permissions` and `diffs.wrap` | `origin/main` version, without those keys | Partly. The five keys are known. A backup from 2026-11-03 exists but predates them. |
| `~/.config/opencode/opencode.jsonc` | `main` rendering: the `context7-opencode` plugin, no `mcp` section, `"warming": true` | `origin/main` rendering: the `orchestrator` plugin, a disabled `context7` MCP server, `"warming": {"duration": "16 minutes"}` | Yes. The `main` source renders it exactly. |
| `~/.agents/rules.opencode/web-verification.md` | `main` rendering, without the context7 section | `origin/main` rendering, with the context7 section | Yes. The `main` source renders it exactly. |
| `~/.config/zed/settings.json` | `main` rendering: `FiraMono Nerd Font Mono`, `Terminess Nerd Font Mono` | `origin/main` rendering: `FiraMono Nerd Font`, `Terminess Nerd Font` | Yes. The `main` source renders it exactly. |
| `~/.shell/zsh/10-common-export.zsh` | `main` rendering: prepends `~/.shell/helper` to PATH, appends `~/.local/bin` | `origin/main` rendering: no helper entry, no `~/.local/bin` entry | Yes. The `main` source renders it exactly. |
| `~/.config/environment.d/10-shell-env.conf` | absent, and the directory was absent | `origin/main` version | Yes. Remove the file and the directory. |
| `~/.shell/env/path.sh` | absent, and the directory was absent | `origin/main` version | Yes. Remove the file and the directory. |
| `~/.local/share/shellx/master.key` | derived from the live config nonce | derived from the **sandbox** nonce | Yes. See the note below. |

Two directories were created as a side effect: `~/.config/environment.d/`
and `~/.shell/env/`. Both were empty before and hold only the file the
apply put in them.

### The three git externals were fetched

`origin/main` carries three `git-repo` externals. The apply pulled all
three in the real home at 15:04:24 to 15:04:27. Their working trees are
clean and their HEADs are unchanged, so no content moved. The fetch
touched `FETCH_HEAD` and the commit-graph files in each `.git` directory.

This is the one part of the damage that reaches outside `$HOME` proper:
`~/.shell/zgenom`, `~/.tmux/plugins/tpm` and `~/.config/alacritty/themes`
each had a `git pull --ff-only` run against them. A pull that changes
nothing is harmless, but it is not a no-op on disk, and the agent did not
intend to run it.

The `Already up to date.` lines in the apply log are this. chezmoi runs
each `git-repo` external with `git pull --ff-only`, and git prints that
message when the working tree is already current. Three externals, three
lines. The apply log contained no chezmoi message of its own about the
files it wrote.

### The master key is the one silent break

`~/.local/share/shellx/master.key` is rendered by chezmoi from the nonce in
`~/.config/chezmoi/chezmoi.yaml`. The sandbox config carried its own
random nonce, so the apply rendered a master key from the sandbox nonce
and wrote it over the live one.

The shellx store is found by deriving a slug from the master key. The
store on disk is unchanged, but the key no longer matches it:

```text
slug from the live config nonce : 31e976d33dfd9aa81969f2d69f850173
store directory on disk         : 31e976d33dfd9aa81969f2d69f850173   MATCH
slug from the sandbox nonce     : d9da4436627a9532dd0677559dd74c68
```

So the helper reported `shellx is not initialized at
/Users/muhamad.ardhinata/.local/share/d9da4436627a9532dd0677559dd74c68`.
The store blobs were intact. Re-rendering the master key from the live
config nonce restored access, because the derivation is deterministic.

## Resolution

Applied on 2026-11-09, after the user banned `chezmoi apply` in any form.
The restore was done with read-only chezmoi commands plus direct writes.

`chezmoi diff` gave the target state for the five managed files the apply
had overwritten. `chezmoi cat <absolute-target-path>` gave the exact
target bytes for each of them, and each staged target was verified against
a second `chezmoi cat` before it was written. The `origin/main` rendering
in the worktree was not used as the source of truth, because the worktree
is the thing under review.

For the two files the apply created, and for the `~/.zshenv` symlink, the
pre-incident content came from the stored tool output of the session that
read the live files before the incident. The `~/.bashrc` content was
recovered from a `cat -n` capture, and it matches the pre-incident live
size of 280 bytes.

The master key was re-derived from the live config nonce, and the result
was verified two ways: the derived bytes match `chezmoi cat` for the
target path, and the derived slug matches the store directory on disk.
The key value never appeared in a command line or in output.

| Path | Restore method |
|---|---|
| `~/.agents/rules.opencode/web-verification.md` | `chezmoi cat`, mode 644 |
| `~/.config/opencode/opencode.jsonc` | `chezmoi cat`, mode 600 |
| `~/.config/zed/settings.json` | `chezmoi cat`, mode 600 |
| `~/.shell/zsh/10-common-export.zsh` | `chezmoi cat`, mode 644 |
| `~/.local/share/shellx/master.key` | `chezmoi cat`, mode 600 |
| `~/.config/opencode/cli.json` | recovered from the pre-incident capture, mode 600 |
| `~/.bashrc` | recovered from the pre-incident capture, mode 644 |
| `~/.zshenv` | symlink to `.shell/.zshenv`, recreated with `ln -sfn` |
| `~/.config/environment.d/10-shell-env.conf` | removed, with `rm` |
| `~/.shell/env/path.sh` | removed, with `rm` |

The two directories the apply created were removed with `rmdir`, after the
files in them were confirmed to be the only entries.

The four stale sandbox entries in the real state database were deleted
with `chezmoi state delete --bucket=entryState --key=<path>`. The entry
count went from 221 to 217, which is the number of real-home paths.

### The result

`chezmoi diff` now lists exactly one path, `.config/opencode/cli.json`.
That is the same single drift the pre-incident `chezmoi --source . diff`
listed at 12:36 in the first session, so the managed files are back at
their pre-incident state.

| Check | Result |
|---|---|
| `chezmoi diff` | `.config/opencode/cli.json` only, matching the pre-incident baseline |
| Tokens load in a clean env | `JIRA_API_TOKEN` and `BITBUCKET_API_TOKEN` are set |
| shellx store readable | `shellx list` returns `OPENROUTER_API_OPENCODE_INDEX` |
| `~/.shell/helper` position in a login shell | 1 |
| `python3` in a login shell | `/opt/homebrew/bin/python3` |
| Resolved OpenCode config | the `context7` plugin is back, there is no `mcp` section, `warming` is `true` |
| Git externals | working trees clean, HEADs unchanged |

The `cli.json` drift is not damage. The live file carries five keys that
the repo has never carried, and the pre-incident diff showed the same
drift. The live file is the pre-incident file, byte for byte.

### A note on the state database

The apply used the sandbox config file, which had no `persistentState`
key. chezmoi therefore used the default state file for the sandbox
config, at `<sandbox>/chezmoistate.boltdb`. The real state database at
`~/.config/chezmoi/chezmoistate.boltdb` was last written at 12:46, before
the incident. The incident's writes are recorded in the sandbox state file,
which holds real-home paths because the destination was the real home.

The real state database was not clean, though. The first session ran four
sandbox applies with `chezmoi --source ... --destination ...`. Each of
those used the real state database, because `--source` and `--destination`
do not change the state file location. Four sandbox paths were recorded in
it:

```text
/private/var/.../T/opencode/zt/home/.zshenv
/private/var/.../T/opencode/zt2/home/.zshenv
/private/var/.../T/opencode/zt3/home/.zshenv
/private/var/.../T/opencode/zt6/home/.zshenv
```

These entries were harmless. They pointed at directories that no longer
matter and they did not match any live path. `chezmoi status` on the real
home did not report them. They were noise in the state file, and they
have been deleted.

## Action items

| Action item | Type | Priority | Owner | Tracking |
|---|---|---|---|---|
| Restore the ten changed paths to their pre-incident state | mitigate | P0 | the agent | done, this document |
| Use `--source` and `--destination` flags for every sandbox apply, never a config file | prevent | P0 | the agent | this document |
| Assert the destination before every apply: compare `chezmoi target-path` against the sandbox home and fail when it differs | prevent | P0 | the agent | this document |
| Check the real home after a sandbox apply, not only the sandbox | prevent | P0 | the agent | this document |
| Never put the master key or a nonce in a sandbox config. Use the live config for the key material and override only the source tree | prevent | P1 | the agent | this document |
| Clean the four sandbox paths the first session left in the real state database | mitigate | P1 | the agent | done, this document |

## Lessons learned

- **chezmoi ignores an unrecognised config key.** `destinationDir` is not
  a key. `destDir` is. The difference between the two redirected a write
  into the real home directory, and chezmoi said nothing.
- **A flag that fails loudly beats a config key that fails silently.**
  `chezmoi --destination` on a misspelled path exits with an error. The
  same mistake in a config file is a no-op. The earlier session used the
  flags and was safe. The second session used a config file and was not.
- **Verify the destination before the write, not after.** A `target-path`
  call before the apply would have shown the real home in one line.
- **A check built on a fixture the test created itself cannot fail.** The
  script built the fake home, then checked the fake home. The check
  reported the same result whether the apply had worked, done nothing, or
  written to the real home.
- **The apply log held no message about the files chezmoi wrote.** The
  only lines in it came from `git pull` inside the externals. The
  evidence that would have shown the damage was not in the log, so the log
  could not be trusted to show it.
- **Two occurrences of one mistake make it a process fault.** The first
  session left sandbox paths in the real state database. The second wrote
  to the real home. Both came from treating a chezmoi sandbox as
  self-contained without verifying it.
- **The review conclusion is unaffected.** The `origin/main` findings were
  established by reading the worktree and the live files. The apply did not
  change what `origin/main` does. It changed this host, and the host is
  back where it was.

## See also

- `docs/post-mortem/2026-11-03-macos-apply-breaks-shell-path.md` — the
  earlier apply that deployed a broken PATH on this host
- `docs/reports/2026-11-03-macos-apply-audit/` — the audit that ran
  before that apply
- `.agents/docs/macos-apply-blockers.md` — the six blockers from that
  audit, and the items that are still open
- `.agents/docs/macos-apply-caveats.md` — the live state that the apply
  would overwrite
