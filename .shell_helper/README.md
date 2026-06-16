# .shell_helper

Helper scripts used by chezmoi templates during source-state evaluation. Scripts here are not applied to the target filesystem.

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

**Target path derivation:**

Source-relative paths are converted to target paths by stripping chezmoi
attribute prefixes (`encrypted_`, `private_`, `readonly_`, `empty_`,
`executable_`, `dot_`) and suffixes (`.tmpl`, `.age`, `.asc`), and converting
`dot_` directory prefixes to `.`.
