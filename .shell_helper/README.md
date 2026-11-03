# .shell_helper

Source-only helper scripts for this repo. Nothing here is applied to the
target filesystem.

`check_decrypt.sh` is the one script that chezmoi itself runs. `.chezmoiignore`
calls it through the `.source_structure.helper` data variable. The other
scripts are operator tools that you run by hand.

## Tools

### `check_decrypt.sh`

Determines which `encrypted_*` files in a source directory can be decrypted with
the available age identities. Used by `.chezmoiignore` to skip encrypted files
whose keys are not present in `.encryption_keys/`.

**Usage:**

```
check_decrypt.sh <KEY_DIR> <SEARCH_DIR>
```

| Argument     | Description                                      |
| ------------ | ------------------------------------------------ |
| `KEY_DIR`    | Path to `.encryption_keys/` directory            |
| `SEARCH_DIR` | Source directory to scan for `encrypted_*` files |

**Behavior:**

- If no `*.secret.key` files exist in `KEY_DIR`, outputs target paths for all
  `encrypted_*` files immediately (no decryption attempts).
- Otherwise, tests each `encrypted_*` file with `age --decrypt` using every
  available identity. Files that fail decryption are output as target paths.
- Output is one line per file, suitable for use as `.chezmoiignore` patterns.

**Skipped directories:**

The scan prunes dot-directories, except `.chezmoi*`. Chezmoi ignores every
dot-directory at the source root except `.chezmoi*`, so a file inside one can
never become a target and never needs an ignore pattern. The prune is what
keeps the script fast: without it the walk descends into `.tmp`, which holds
well over a hundred thousand files, on every chezmoi command.

**Target path derivation:**

Source-relative paths are converted to target paths the way chezmoi does it.
Each path component is stripped of the source-state attributes that apply to
it, in the order chezmoi parses them:

| Component | Attributes, in order |
| --- | --- |
| Directory | `remove_`, `external_`, `exact_`, `private_`, `readonly_`, `dot_` |
| File | `encrypted_`, `private_`, `readonly_`, `empty_`, `executable_`, `dot_` |

`dot_` becomes a leading dot rather than being removed. `literal_` stops
attribute parsing and may appear anywhere. The suffixes `.age`, `.tmpl` and
`.literal` are stripped outermost first.

The mapping must agree with `chezmoi target-path` exactly. A mismatch means
the ignore pattern misses the real target and `chezmoi apply` dies on the
undecryptable file. Run `bash .shell_helper/test_check_decrypt.sh` to check it
against the source tree.

### `backup_targets.sh`

Copies the live targets that a `chezmoi apply` would change, so the apply can
be undone. The backup holds the **current destination state**, not the target
state.

**Usage:**

```
backup_targets.sh <backup-dir>
backup_targets.sh --restore <backup-dir>
```

Set `CHEZMOI_CONFIG` to point at a config file when the default config cannot
render the target state.

**Backup layout:**

| File | Contents |
| --- | --- |
| `manifest.tsv` | Status code, target path, live path. One line per changed target. |
| `files/` | A copy of each live target that is a file or a symlink. |
| `metadata.tsv` | Kind, mode, target path. One line per recorded path. |

**Behavior:**

- Reads `chezmoi status` to find the changed targets.
- Copies files and symlinks. A symlink is stored as a symlink, not as a copy
  of its target.
- A directory is recorded as a mode only. `chezmoi status` lists a changed
  directory and its changed files as separate entries, so copying the
  directory would pull in the whole tree. That matters for `~/Library`.
- `--extra <path>` adds a path that chezmoi does not manage but that the
  apply would disturb. The path is relative to `$HOME`. Use it for
  hand-written files inside a directory whose mode the apply changes.
- The restore copies the files back and restores the modes. It does not
  remove files the apply created. Remove those with `chezmoi destroy`.

**Portability:**

The script runs on macOS and on Linux. It reads the permission bits with
`stat_mode`, which picks the BSD `-f` or the GNU `-c` form. Both print the
same octal string, so the value feeds `chmod` unchanged.

The script takes its target list from `chezmoi status`, so it works on any
host with a chezmoi config. The `--extra` paths are host-specific: on a
host where chezmoi manages a file, the file is already in the list and
needs no `--extra`.
