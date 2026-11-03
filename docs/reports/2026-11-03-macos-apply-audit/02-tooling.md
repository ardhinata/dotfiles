# The tooling written for the macOS apply

Two source-only helper scripts came out of the audit. One fixes a bug that
would stop the apply. The other makes the apply reversible.

**Status: both in the working tree, staged, not committed.** The
canonical source of truth for this repo lives on another machine, so the
changes are left uncommitted for the owner to sync.

Back to the [report index](README.md).

## The `check_decrypt.sh` path-mapping bug

### Summary

`.shell_helper/check_decrypt.sh` builds the ignore patterns that keep
undecryptable files out of an apply. It mapped the chezmoi source-state
attributes on the file name only, not on the directory components. One
encrypted file escaped its ignore pattern, and the apply died on it.

### Steps to reproduce

1. Take a source tree that holds an encrypted file under a directory with
   a `private_` attribute.
2. Run `.shell_helper/check_decrypt.sh` with the key directory and the
   source directory.
3. Compare the printed target path with `chezmoi target-path` for the
   same source file.
4. Observe the two paths differ.

### Expected

The helper prints the same target path that chezmoi would use.

### Actual

The helper printed `.shell/private_store/personal-laptop_environment_store.json`.
chezmoi maps that source file to
`.shell/store/personal-laptop_environment_store.json`.

The ignore pattern missed the real target, so chezmoi tried to decrypt
the file during the apply and failed.

### Environment

| Part | Value |
|---|---|
| chezmoi | v2.74.0, Homebrew |
| Helper | `.shell_helper/check_decrypt.sh` |
| Affected files | 25 encrypted files in the source tree |
| Attribute combinations tested | 228 |

### Impact

The apply could not run at all on a host without the age identity. The
host is the macOS work laptop, which must not have the identity, because
the encrypted files are the personal machine's SSH keys. The helper is
the mechanism that lets such a host skip them, so the bug removed the
only safe path forward.

### Suspected cause

The mapping applied the attribute strip to the last path component only.
chezmoi applies it to each component in turn. A `private_` on a
directory changes the directory mode and does not change the directory
name. But a `private_` on a directory component is still a component
attribute, and a later `dot_` maps it to a leading dot.

This cause was verified, not guessed. The rewrite now reproduces
chezmoi's parse order exactly.

### The fix

The mapping was rewritten to strip the attributes that apply to each
component, in the order chezmoi parses them:

| Component | Attributes, in order |
|---|---|
| Directory | `remove_`, `external_`, `exact_`, `private_`, `readonly_`, `dot_` |
| File | `encrypted_`, `private_`, `readonly_`, `empty_`, `executable_`, `dot_` |

`dot_` becomes a leading dot rather than being removed. `literal_` stops
attribute parsing and may appear anywhere. The suffixes `.age`, `.tmpl`
and `.literal` are stripped outermost first.

The rules were established empirically, against `chezmoi target-path`,
rather than from the documentation. The documentation does not state the
per-component parse order. Guessing it produced a mapping that diverged
from chezmoi in several more cases than the original bug.

### Verification

`chezmoi target-path` for all 25 encrypted files, plus 228 attribute
combinations across a matrix of source-state attributes. Every generated
path matched chezmoi exactly.

`.shell_helper/test_check_decrypt.sh` is the regression check. It pairs
the helper output with `chezmoi target-path` by `find` order, and it
fails against the original implementation.

```text
$ bash .shell_helper/test_check_decrypt.sh
OK: 25 encrypted files map to the chezmoi target path
```

The check is what the audit was missing. The bug survived because
nothing compared the helper output with chezmoi's own answer.

## The `backup_targets.sh` backup tool

### Summary

A `chezmoi apply` overwrites files in the home directory. Nothing in the
repo could reverse that. `backup_targets.sh` copies the live state of
every target an apply would change, so the apply can be undone.

### Usage

```bash
CHEZMOI_CONFIG=<config> .shell_helper/backup_targets.sh <backup-dir> \
  [--extra <path-relative-to-HOME> ...]
.shell_helper/backup_targets.sh --restore <backup-dir>
```

The backup dir receives `manifest.tsv` (the status code and the target
path), `files/` (a copy of each live file and symlink) and
`metadata.tsv` (the kind, the mode, and the path).

### Three traps it handles

**Directories must be recorded as a mode only.** `chezmoi status` lists a
changed directory and its changed files as separate entries. Copying the
directory pulls in the whole tree. The first version of the script did
that, and it tried to copy `~/Library` and the sockets under it. The
script now records the mode and copies each file individually.

**Symlinks must not be dereferenced.** The live `~/.zshrc` is a symlink
to `~/.shell/.zshrc`. The backup stores a symlink, not a copy of the
target, and the restore recreates the link.

**The restore cannot delete what the apply created.** It copies files
back and restores the modes. Files the apply creates need
`chezmoi destroy <target>`.

### The `--extra` flag

The `--extra` paths are files that chezmoi does not manage but that the
apply disturbs. On this host they are the four `~/.ssh/config.d/*.conf`
fragments, which live in a directory whose mode the apply changes. On a
host where chezmoi manages those files, they are already in the list and
need no `--extra`.

### Why it is worth tracking

It is the only undo mechanism for `chezmoi apply`. The repo's existing
practice, in `docs/chezmoi-migrate.md`, was a manual whole-host copy of
about 1.5 GB. This is the per-target version: 1.5 seconds and 236 KB for
the 53 targets on this host.

It also encodes three traps that are not visible in the code. Anyone who
rewrites the script hits all three again.

### Why it is worth making portable

The script derives its target list from `chezmoi status`, so it is
host-agnostic by design. The first version was not portable. It used
BSD `stat -f '%Lp'` in two places, which does not exist on the Linux
host. The Linux host is where the canonical source lives, so a
macOS-only script in a shared repo is a trap.

The fix is a probe that picks the right form:

```bash
if stat -f '%Lp' /dev/null >/dev/null 2>&1; then
	stat_mode() { stat -f '%Lp' "$1"; }
else
	stat_mode() { stat -c '%a' "$1"; }
fi
```

Both forms print the same octal string, so the value feeds `chmod`
unchanged.

The GNU branch was verified with a GNU-style `stat` stub on `PATH`. The
test ran a full backup, mutate and restore cycle in a scratch home
directory. A file mode came back from `666` to `600`, and a directory
mode came back from `755` to `700`. The BSD branch produces a
`metadata.tsv` that is byte-identical to the backup taken before the
change.

Everything else was already portable: `readlink`, `cp -p`, `ln -s`, `wc`,
`dirname`, and the `chezmoi status` output format.

### Where it sits

`.shell_helper/` is a source-only directory. Nothing in it is deployed to
the target filesystem. The dir carries a chezmoi data variable,
`.source_structure.helper`, and `.chezmoiignore` uses it to find
`check_decrypt.sh`. That one script is the only file in the dir that
chezmoi itself runs. The rest are operator tools.

## What changed in the working tree

| Path | Change |
|---|---|
| `.shell_helper/check_decrypt.sh` | The mapping rewritten to strip attributes per component |
| `.shell_helper/test_check_decrypt.sh` | New. The regression check |
| `.shell_helper/backup_targets.sh` | New. The backup and restore tool |
| `.shell_helper/README.md` | Both scripts documented, with the portability note |
| `.agents/docs/macos-apply-blockers.md` | New. The six blockers |
| `.agents/docs/macos-apply-target-state.md` | New. The 53 targets |
| `.agents/docs/macos-apply-caveats.md` | New. The non-blocking changes |
| `.agents/docs/macos-host-handoff.md` | The backup step and the troubleshooting rows |
| `docs/reports/2026-11-03-macos-host-portability.md` | The instruction to copy the personal age identity removed |
| `README.md` | The `config.d` classification convention |

All ten files are staged. No commit was made.

## What was not checked

`ruff` is not installed on this host, so the linter named in `AGENTS.md`
could not run. No Python was changed in this work, so the gap did not
matter, but it is a gap.

The `restore` path copies files and restores modes. It does not record
the owner, so a target owned by root would come back owned by the
invoking user. No target on this host is root-owned.
