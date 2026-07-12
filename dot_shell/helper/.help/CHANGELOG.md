# Changelog

All notable changes to `shellx` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] — 2026-07-12

### Added

- Initial release of `shellx`, replacing the legacy `runpriv` /
  `encrypt_store.sh` bash helpers.
- Pure-Python-3-stdlib implementation (no pip, no venv).
- `init` subcommand for first-time store setup.
- `store`, `list`, `rm` subcommands for managing entries.
- `--tag=…` and `-- proc …` exec mode for runtime secret injection.
- `export` subcommand emitting JSONC encrypted by `chezmoi encrypt`.
- `import` subcommand using `chezmoi decrypt` for `.age` files.
- AEAD-equivalent crypto: scrypt → ChaCha20 + HMAC-BLAKE2b with
  variable-name binding in the AAD.
- Zsh completion (`_shellx`) with tag and var-name candidates.
- Random 16-hex slug directory under `~/.local/share/`.
- This documentation set in `dot_shell/helper/.help/` (source-only).

### Changed

- (none yet)

### Deprecated

- `runpriv` and `encrypt_store.sh` are superseded by `shellx` but remain
  in the repo until the next major version. They will be removed in
  `shellx 2.0`.

### Removed

- (none yet)

### Fixed

- (none yet)

### Security

- See [`CRYPTO.md`](./CRYPTO.md) and [`LIMITATIONS.md`](./LIMITATIONS.md)
  for the threat model and what this version does and does not defend
  against.

## Migration notes

There is **no automatic migration** from the legacy JSON store. Users
who have existing `runpriv`-managed secrets should:

1. `shellx init` (creates the new store).
2. Re-add each secret with `shellx store VAR --tag=… --process=…`.
3. Optionally, run `shellx export` to back up the new store.

The legacy helpers remain functional and can be invoked alongside
`shellx` for backward compatibility during transition. They read from
`~/.shell/store/<profile>_environment_store.json` while `shellx` reads
from `~/.local/share/<slug>/.idx`.

## Future plans

- **`shellx 1.1`** — `shellx rotate VAR` to generate a new random value
  via `secrets.token_urlsafe(N)` for cases where the API supports
  self-issued tokens.
- **`shellx 1.2`** — optional `--age` flag on `store` to also age-encrypt
  the blob (defense-in-depth for the live store).
- **`shellx 2.0`** — remove the legacy bash helpers, change the store
  layout to require explicit init confirmation, add Argon2id option.