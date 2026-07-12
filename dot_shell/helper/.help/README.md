# shellx — stealth-first secret manager

`shellx` is the replacement for the legacy `runpriv` / `encrypt_store.sh`
helpers. It stores environment-variable secrets (API tokens, deploy keys,
etc.) encrypted at rest and injects them into a target process only at the
moment of launch, so they never appear in your shell history, your
persistent env, or your shell rc files.

The threat model is **cheap static analysis and signature-based scans** by
basic infostealers or rogue user-level processes: greps over `~` for
`token|secret|cred|key` paths, sweeps of `~/.aws/`, `~/.config/gh/*`,
`~/.npmrc`, `~/.netrc`, etc., and `/proc/<pid>/environ` reads against
visible processes.

See `LIMITATIONS.md` for what shellx does *not* defend against.

## Why a new design

| Old helper | New `shellx` |
|---|---|
| Bash + `openssl enc` + `jq` | Python 3 stdlib only (no `pip`, no venv) |
| Plaintext JSON store at `~/.shell/store/` | Opaque binary blobs at `~/.local/share/<random-slug>/` |
| Filename `store/<profile>_environment_store.json` greps as a credential file | Slug is random 16 hex; blob names are `blake2b(VAR+slug)` hex — indistinguishable from app cache noise |
| `runpriv` is recognizable by name | `shellx` is a single, neutral binary |
| ChaCha20 stream cipher without authentication | scrypt KDF → ChaCha20 + HMAC-BLAKE2b (AEAD-equivalent construction) |
| No round-trip with the chezmoi source tree | `export` / `import` subcommands produce JSONC encrypted by `chezmoi encrypt` / `chezmoi decrypt` |

## Quick start

```bash
# 1. First run initializes the store automatically (after `chezmoi apply`).
shellx init

# 2. Add a secret (value is read from stdin, or prompted if stdin is a TTY).
echo -n 'ghp_xxxxxxxxxxxxxxxxxxxx' | shellx store GH_TOKEN --tag=git,api --process=gh,glab

# 3. List what's stored.
shellx list

# 4. Run a command with the matching secrets injected into its env.
shellx --tag=git gh pr list      # injects GH_TOKEN (and any other --tag=git vars)

# 5. Export to the chezmoi source tree (creates encrypted_*.jsonc.age).
shellx export

# 6. Restore on another machine.
shellx import ~/.local/share/chezmoi/.encrypted_data/tokens/encrypted_*.jsonc.age
```

## Subcommands

| Command | Purpose |
|---|---|
| `shellx` (no args) | If uninitialized: auto-init. Else: print help. |
| `shellx init` | Create `~/.local/share/<slug>/` with `.sl` (slug) and `.idx` (index). |
| `shellx store VAR --tag=a,b --process=x,y` | Encrypt value from stdin → blob + idx entry. |
| `shellx list` | Print `VAR → tags/processes/updated`. |
| `shellx rm VAR` | Remove blob + idx line. |
| `shellx export [--to DIR] [--label LABEL] [--no-encrypt]` | Generate JSONC, pipe through `chezmoi encrypt` to `<source>/.encrypted_data/tokens/encrypted_*.jsonc.age`. |
| `shellx import PATH [--to DIR] [--slug S] [--force] [--dry-run]` | `chezmoi decrypt` + parse JSONC, re-encrypt into the live store. |
| `shellx --tag=a,b -- proc args…` | Exec `proc` with matched secrets injected. |
| `shellx -- proc args…` | Exec `proc` with secrets whose `process` list includes `proc`. |

## Files

| Path (chezmoi source) | Purpose |
|---|---|
| `dot_shell/helper/executable_shellx.tmpl` | The Python 3 launcher + all subcommands. |
| `dot_shell/helper/executable_shellx_completion_helper.tmpl` | Tiny stdlib helper used by the zsh completion. |
| `dot_shell/helper/.help/` | This documentation set (source-only — excluded from `chezmoi apply`). |
| `dot_shell/zsh/completions/_shellx.tmpl` | zsh completion (`#compdef shellx`). |
| `.encrypted_data/tokens/` | Default export destination. `shellx export` writes `encrypted_*.jsonc.age` here. |
| `.chezmoiscripts/run_onchange_init-shellx-store.sh` | Post-apply hook that enforces `~/.local/share/` permissions. |
| `.chezmoiignore` | `dot_shell/helper/.help` keeps docs source-only; `.encrypted_data/tokens/shellx*` prevents auto-restore of exports on apply. |

## Live (runtime) layout

```
~/.local/share/<random-16-hex-slug>/
├── .sl          # 16-hex slug (sanity check; same as dir name)
├── .idx         # plaintext index: VAR<TAB>tags<TAB>procs<TAB>updated
└── <16-hex>     # per-secret opaque blob (filename = blake2b(VAR,slug)[:8])
~/.shellx-store  # single line: absolute path to the store dir above
```

## Dependencies

- **Python 3** ≥ 3.8 (uses `hashlib.scrypt`, `secrets.token_bytes`, `hmac.blake2b`).
- **`age`** — used transitively via `chezmoi encrypt` / `chezmoi decrypt` for
  export/import. Runtime secret injection (`--tag=… -- proc …`) does
  **not** need `age`.
- **`chezmoi`** — needed for export (uses `chezmoi encrypt --output` and
  `chezmoi source-path`) and import (uses `chezmoi decrypt`).
- No pip, no venv, no `site-packages/cryptography`.

## Documentation index

- [`INSTALL.md`](./INSTALL.md) — first-time setup, onboarding, and CI.
- [`CRYPTO.md`](./CRYPTO.md) — cipher suite, key derivation, blob format, and AAD construction.
- [`JSONC_FORMAT.md`](./JSONC_FORMAT.md) — exact JSONC schema with header and inline comments.
- [`EXPORT_IMPORT.md`](./EXPORT_IMPORT.md) — export/import workflow, chezmoi source path detection, key handling.
- [`LIMITATIONS.md`](./LIMITATIONS.md) — what shellx does and does not defend against.
- [`CHANGELOG.md`](./CHANGELOG.md) — release notes.

## Design rationale (one-liner)

> A static scanner shouldn't be able to find your secrets by path, filename,
> or content — and a process tree observer shouldn't see them at rest.
> Secrets exist as opaque ciphertext on disk, in shell history never,
> and in `/proc/<pid>/environ` only for the lifetime of the child that
> asked for them.