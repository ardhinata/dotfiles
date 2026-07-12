# Export / Import

`shellx` round-trips the encrypted store through the chezmoi source tree
via JSONC files encrypted with `age`. This lets you commit an export to
a remote dotfiles repo, restore it on another machine, or audit the
metadata in a plain-text editor.

## Why JSONC, not JSON

JSONC is JSON with `//` line comments. Editors (VSCode, vim with jsonc
plugin, IntelliJ) highlight it without errors and you can embed
human-readable metadata that the importer can parse:

```jsonc
// shellx_export: true
// shellx export — DO NOT EDIT by hand. Re-export with `shellx export`.
// Format version: 1
// Hostname:        desktop-main
// Profile:         personal-laptop
// Slug:            a3f9c1d8
// Exported at:     2026-07-12T10:41:44+07:00
// Shellx version:  1.0.0
// Original path:   /home/user/.local/share/a3f9c1d8
{
  // var: GH  tags: ["git","api"]  processes: ["gh","glab"]  updated: 2026-07-11T22:10:03+07:00
  "GH": {
    "value": "ghp_xxxxxxxxxxxxxxxxxxxx",
    "tag": ["git", "api"],
    "process": ["gh", "glab"]
  }
}
```

The `value` field is the **plaintext secret** during the brief lifetime
of the file. By default `shellx export` never lets the plaintext JSONC
touch disk — it pipes through `chezmoi encrypt` directly. Only when you
pass `--no-encrypt` does the plaintext version get written (for review
or manual commit, with a loud stderr warning).

## Filename convention

Exports follow the chezmoi `encrypted_` source-state prefix convention:

```
.encrypted_data/tokens/encrypted_<host>_<slug>_<utc-timestamp>.jsonc.age
```

Example:
```
.encrypted_data/tokens/encrypted_desktop-main_a3f9c1d8_20260712T034144Z.jsonc.age
```

When you `chezmoi add` this file, it remains encrypted at rest and is
excluded from `chezmoi apply` by the `.encrypted_data/tokens/shellx*`
rule in `.chezmoiignore`. Restore is **explicit** via `shellx import`.

## Export workflow

```bash
# Default: writes encrypted_*.jsonc.age to <source>/.encrypted_data/tokens/
shellx export

# Custom destination:
shellx export --to /tmp/backups

# Custom label (replaces <host>_<slug>_<utc> in the filename):
shellx export --label manual-backup-2026-07

# Audit the JSONC without committing (WARNING: writes plaintext):
shellx export --no-encrypt --to /tmp/audit
less /tmp/audit/encrypted_*.jsonc
```

### How the default destination is discovered

1. `$CHEZMOI_SOURCE_PATH` environment variable (if set).
2. `chezmoi source-path` subprocess (preferred — guaranteed correct).
3. Fallback: `~/.local/share/chezmoi/.encrypted_data/tokens/`.

If chezmoi is unavailable and the env var is unset, the fallback is used
silently.

### How encryption happens

1. Build JSONC in memory.
2. Pipe plaintext to `chezmoi encrypt --output <dest>` via subprocess.
   `chezmoi encrypt` writes ciphertext to the file at `<dest>` and uses
   the age recipients from `chezmoi.yaml`.
3. The plaintext is scrubbed from memory after the subprocess returns.
4. The `.age` file is chmod'd 600 at the destination.

If `chezmoi encrypt` fails (e.g., no recipients configured), the
subprocess's stderr is surfaced and the command exits non-zero.

## Import workflow

```bash
# Restore from the default chezmoi source tree:
shellx import ~/.local/share/chezmoi/.encrypted_data/tokens/encrypted_*.jsonc.age

# Restore from a custom location:
shellx import /tmp/backups/encrypted_*.jsonc.age

# Dry-run (no writes):
shellx import --dry-run /path/to/encrypted_*.jsonc.age

# Overwrite existing entries (default: skip on conflict):
shellx import --force /path/to/encrypted_*.jsonc.age

# Restore into a different store directory:
shellx import --to ~/.local/share/NEW_SLUG /path/to/file.jsonc.age
```

### How decryption happens

For `.age` files, `shellx import` shells out to `chezmoi decrypt`. Chezmoi
uses the age identities configured in `~/.config/chezmoi/chezmoi.yaml` —
no separate `AGE_IDENTITY_FILE` setup is required, because chezmoi
already knows which keys can decrypt which recipients.

### Import conflict policy

| Existing entry | `--force` flag | Result |
|---|---|---|
| absent | — | Added |
| present | absent | **Skipped** (with summary at end) |
| present | present | Overwritten with imported value + metadata |

After import, the `.idx` index is rewritten to include all imported
entries plus any pre-existing entries that were not in the export.

### Round-trip guarantee

For a same-profile import, every `shellx --tag=… -- proc …` invocation
that worked before the export will work identically after the import.

A cross-profile import (different `STATIC_PW`) will decrypt the JSONC
fine (the JSONC is plaintext), but the import-side encryption uses the
**target machine's** `STATIC_PW`. So a `home` export imported on a
`work-laptop` machine becomes a `work-laptop` store. The profile name
in the JSONC header is informational only.

## Schema versioning

The `shellx_export: true` and `Format version: N` header lines are
required and parsed by importers. Current version: **1**. A future `2`
may add fields; importers must reject unknown major versions.

## Operational notes

- **No plaintext at rest**: by default, `shellx export` does not leave
  plaintext on disk. Only use `--no-encrypt` for ephemeral review.
- **No dedup**: each entry is encrypted as its own blob (so individual
  entries can be decrypted independently). An export contains all of
  them in one JSONC for portability.
- **Idempotent re-exports**: running `shellx export` twice produces two
  files with different timestamps. Old files should be cleaned up
  manually (`git rm`) to avoid leaving stale snapshots.
- **No automatic re-import**: this is intentional. A fresh `chezmoi
  apply` on a new machine should not silently restore a secret store.