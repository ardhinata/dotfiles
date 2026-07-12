# `.encrypted_data/tokens/`

This directory holds **age-encrypted secret snippets** that are
checked into the chezmoi source tree. Two kinds of files live here:

## 1. Per-profile shell snippets (manual)

Naming: `<profile>_<name>.zsh.age` (e.g., `personal-laptop_github.zsh.age`).

These are short shell snippets containing `export VAR="value"` lines.
They are sourced at shell startup by `dot_shell/zsh/00-before-zgenom.zsh`
when the current profile matches. See the **Machine profiles** section
of the top-level README.

## 2. `shellx` exports (auto-generated)

Naming: `encrypted_<host>_<slug>_<utc-timestamp>.jsonc.age`.

Created by `shellx export` (see
[`dot_shell/helper/.help/EXPORT_IMPORT.md`](../../dot_shell/helper/.help/EXPORT_IMPORT.md)).
These contain the full encrypted secret store in JSONC format, encrypted
via `chezmoi encrypt` with the recipients in `.encryption_keys/`.

`.chezmoiignore` excludes `.encrypted_data/tokens/shellx*` from
`chezmoi apply` — restore is **explicit** via
`shellx import <file>`. A fresh `chezmoi apply` on a new machine will
not silently recreate your secret store.

## Workflow

```bash
# Export from the live store.
shellx export

# Stage the new file.
cd ~/.local/share/chezmoi
git add .encrypted_data/tokens/encrypted_*.jsonc.age

# On another machine, after pulling:
shellx import .encrypted_data/tokens/encrypted_*.jsonc.age
```

See [`dot_shell/helper/.help/`](../../dot_shell/helper/.help/) for
full documentation of the shellx secret manager.