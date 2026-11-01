# shellx — stealth-first secret manager

`shellx` is the replacement for the legacy `runpriv` / `encrypt_store.sh`
helpers. It stores environment-variable secrets (API tokens, deploy keys,
etc.) encrypted at rest and injects them into a target process only at the
moment of launch, so they never appear in your shell history or your shell
rc files. The `env` subcommand is the one exception. It prints an `export`
line for a shell startup file that asks for a variable by name.

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
| Plaintext JSON store at `~/.shell/store/` | Opaque binary blobs at `~/.local/share/<derived-slug>/` |
| Filename `store/<profile>_environment_store.json` greps as a credential file | Slug is a 32-hex blake2b of `STATIC_PW = sha256sum("com.ardju.utils:shellx:" + nonce)`; blob names are `blake2b(VAR + "\0" + slug)[:8]` hex — indistinguishable from app cache noise to a viewer who doesn't know your nonce |
| `runpriv` is recognizable by name | `shellx` is a single, neutral binary |
| ChaCha20 stream cipher without authentication | KDF → ChaCha20 + HMAC-BLAKE2b (AEAD-equivalent construction) |
| No round-trip with the chezmoi source tree | `export` / `import` subcommands produce JSONC encrypted by `chezmoi encrypt` / `chezmoi decrypt` |
| `~/.shellx-store` marker file pointing at the store | No marker — the store path is derived from your nonce, so it is reproducible across machines sharing the same chezmoi config |

## Quick start

```bash
# 1. Initialize the store (one-time, after `chezmoi apply`).
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
shellx import "$(ls -t ~/.local/share/chezmoi/.encrypted_data/env_store/encrypted_*.jsonc.age | head -1)"

# 7. Move the master key into the platform secret store (optional).
shellx key move
```

## Subcommands

| Command | Purpose |
|---|---|
| `shellx` (no args) | Print help. |
| `shellx init` | Create `~/.local/share/<derived-slug>/` with `.sl` (slug) and `.idx` (index). The slug is `blake2b(STATIC_PW)[:16].hex()` — reproducible across machines sharing your chezmoi nonce. |
| `shellx store VAR --tag=a,b --process=x,y` | Encrypt value from stdin → blob + idx entry. |
| `shellx list` | Print `VAR → tags/processes/updated`. |
| `shellx rm VAR` | Remove blob + idx line. |
| `shellx env VAR [VAR…]` | Print one `export VAR=<value>` line per variable, for a shell startup file. The value is quoted, so it stays one shell word. |
| `shellx export [--to DIR] [--label LABEL] [--no-encrypt]` | Generate JSONC, pipe through `chezmoi encrypt` to `<source>/.encrypted_data/env_store/encrypted_*.jsonc.age`. |
| `shellx import PATH [--to DIR] [--slug S] [--force] [--dry-run]` | `chezmoi decrypt` + parse JSONC, re-encrypt into the target store. The index is written into the target directory. |
| `shellx key status` | Print where the master key comes from and a fingerprint. Never prints the key. |
| `shellx key store` | Copy the master key into the platform secret store (the macOS login Keychain, or libsecret elsewhere). |
| `shellx key move` | Copy the master key into the platform secret store and remove the key file. |
| `shellx key clear` | Remove the master key from the platform secret store. |
| `shellx --tag=a,b -- proc args…` | Exec `proc` with secrets matching any tag in `a,b` injected. |
| `shellx --process=NAME -- proc args…` | Exec `proc` with secrets whose `process` list includes `NAME` injected. |
| `shellx -- proc args…` | Shorthand: `proc` is used as the `--process` matcher. |

When both `--tag` and `--process` are given, `--tag` wins (the
`--process` filter is skipped). This is the same precedence as the
legacy `runpriv` helper.

## Files

| Path (chezmoi source) | Purpose |
|---|---|
| `dot_shell/helper/private_executable_shellx.tmpl` | The Python 3 launcher + all subcommands. The `private_executable_` attributes give the target mode 0700, so the helper is not readable by other users. |
| `dot_local/share/shellx/private_master.key.tmpl` | The master key, rendered at apply time as `sha256sum("com.ardju.utils:shellx:<nonce>")`. The `private_` attribute gives the target mode 0600. |
| `dot_shell/helper/executable_shellx_completion_helper.tmpl` | Tiny stdlib helper used by the zsh completion. |
| `dot_shell/helper/.help/` | This documentation set (source-only — excluded from `chezmoi apply`). |
| `dot_shell/zsh/completions/_shellx.tmpl` | zsh completion (`#compdef shellx`). |
| `.encrypted_data/env_store/` | Default export destination. `shellx export` writes `encrypted_<host>_<slug>_<utc>.jsonc.age` files here. |
| `.chezmoiscripts/run_onchange_init-shellx-store.sh` | Post-apply hook that enforces `~/.local/share/` permissions. |
| `.chezmoiignore` | `dot_shell/helper/.help` keeps docs source-only; `.encrypted_data/env_store/shellx*` prevents auto-restore of exports on apply. |

## The master key

The helper holds no secret. It reads the master key at runtime, in this
order:

1. `SHELLX_MASTER_KEY` — an environment override, for tests and for a
   one-off recovery run.
2. `SHELLX_NONCE` — a test-only override that derives the key from a nonce.
3. `~/.local/share/shellx/master.key` — rendered by `chezmoi apply`, mode
   0600.
4. The platform secret store — the macOS login Keychain through
   `security`, or libsecret through `secret-tool` elsewhere.

The key file comes first because it costs a plain read. The secret store
costs a subprocess call, so it is only reached when the file is gone.

Every command needs the key, because the store path is derived from it. A
missing key exits with code 4. The zsh startup loader turns that into a
warning on stderr, so a missing secret never blocks the login.

Run `shellx key move` to move the key into the platform secret store and
remove the file. Then a file scanner never sees the master key.

## Live (runtime) layout

```
~/.local/share/
├── shellx/
│   └── master.key   # the master key, mode 0600 (absent after `shellx key move`)
└── <derived-32-hex-slug>/
    ├── .sl          # 32-hex derived slug (sanity check; equals basename)
    ├── .idx         # plaintext index: VAR<TAB>tags<TAB>procs<TAB>updated
    └── <16-hex>     # per-secret opaque blob (filename = blake2b(VAR + "\0" + slug)[:8], 16 hex chars)
```

The slug is `blake2b(STATIC_PW)[:16].hex()` — 32 hex chars. The directory
name is the slug; the `.sl` file is a redundant copy so a viewer can
verify the directory is "the right one" without re-deriving it. There is
no marker file: any machine with the same chezmoi nonce will compute the
same slug and land at the same path. Legacy stores (1.0–1.4.x) that
have a `.sl` containing a different slug continue to work — see
[`CHANGELOG.md`](./CHANGELOG.md) for the migration note.

## Dependencies

- **Python 3** ≥ 3.10 (uses `hashlib.scrypt`, `hashlib.sha512` through `hmac.new`, `secrets.token_bytes`, `hashlib.blake2b` passed to `hmac.new`, plus PEP 604 `str | None` and PEP 585 built-in generics).
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