# Changelog

All notable changes to `shellx` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **`SHELLX_VARS` env var injected alongside `RUNPRIV_VARS`.** When
  `cmd_exec` injects matching secrets into the launched process, it now
  sets `SHELLX_VARS` to the same comma-separated list of injected
  variable names. `RUNPRIV_VARS` is still set to the same value for
  backward compatibility with consumers written before shellx 1.x.
  Prefer `SHELLX_VARS` in new code; treat `RUNPRIV_VARS` as the legacy
  alias.

## [1.5.0] — 2026-08-24

### Changed

- **`STATIC_PW` derivation moved entirely to apply time.** The deployed
  `executable_shellx` now embeds `STATIC_PW = sha256sum("com.ardju.utils:shellx:<nonce>")`
  as a plain hex string constant. Previously `STATIC_PW = "chezmoi:shellx:<profile>:<nonce>"`
  was assembled at runtime from template-injected `profile` + `nonce`
  (and a `chezmoi data` subprocess fallback for non-templated
  deployments). The new namespace is a reverse-DNS prefix unique to
  shellx, so other tools deriving from the shared `system_environment.nonce`
  can pick their own `com.ardju.utils:<tool>:<nonce>` namespace without
  keyspace collision.
- **`<profile>` removed from `STATIC_PW`.** Profile contributed only a
  few bits of entropy (and was already guessable, e.g. `personal-laptop`).
  The 64-char `randAlphaNum` nonce alone provides ~384 bits. Two
  profiles on one machine now share the same `STATIC_PW` (and therefore
  the same store slug) — see "Side effects" below.
- **`chezmoi data` subprocess fallback removed.** `_load_env()` and its
  four-step resolution chain (cache → env-var → template → subprocess)
  is gone. The deployed script has only one source for the nonce:
  `SHELLX_NONCE` env-var override (test hook) or the template-injected
  `SHELLX_NONCE_DEFAULT`. If both are empty, `shellx` exits with a
  clear "re-run `chezmoi apply`" error — no silent subprocess.
- **Completion helper is now a chezmoi template.** `executable_shellx_completion_helper`
  previously shelled out to `chezmoi data` on every zsh-completion render
  to derive the store slug. As of 1.5.0, it embeds the same derived
  `STATIC_PW` hex at apply time and uses it directly — zero subprocess.
  (Side fix: the helper's `main()` body had been accidentally truncated
  since shellx 1.1.0 (commit `c1701d0`); the body has been restored so
  completion actually emits tags/processes/vars instead of silently
  returning nothing.)

### Migration from 1.4.x

⚠️ **Data-store format is incompatible.** The store slug is
`blake2b(STATIC_PW)[:16].hex()`, and `STATIC_PW` changed. Old stores at
`~/.local/share/<old-slug>/` cannot be decrypted with the new `STATIC_PW`.

1. `chezmoi apply` → regenerates the deployed script with the new
   derived `STATIC_PW`.
2. `python3 -m py_compile ~/.shell/helper/shellx` → sanity check.
3. Wipe the old store: `rm -rf ~/.local/share/<old-slug>/`. (Find the
   old slug with `git show HEAD~1:.chezmoiscripts/run_onchange_init-shellx-store.sh`
   if needed — it's the slug the previous deployed script reported.)
4. `shellx init` → creates the new store at the new slug.
5. `shellx import "$(ls -t ~/.local/share/chezmoi/.encrypted_data/env_store/encrypted_*.jsonc.age | head -1)"`
   → re-encrypts all entries from the age-encrypted export under the
   new `STATIC_PW`. (The export itself is independent of `STATIC_PW` —
   only the import operation re-encrypts.)
6. `shellx list` → sanity check the index is repopulated.

### Side effects

- **No per-profile store isolation.** Two profiles on one machine now
  share the same store path and the same `STATIC_PW`. This was only
  ever defense-in-depth (profile was guessable), and this machine runs
  a single profile — but be aware if you ever set up multi-profile.
- **No CI/headless fallback.** The previous `chezmoi data` subprocess
  allowed non-templated deployments (e.g. CI boxes without `chezmoi`)
  to resolve the nonce at runtime. As of 1.5.0, the only non-templated
  path is `SHELLX_NONCE=<64-char>` in the environment — and the caller
  must also know that `STATIC_PW = sha256sum("com.ardju.utils:shellx:<nonce>")`
  (i.e. the test hook is no longer a CI recovery mechanism).
- **Deployed script leaks the derived hash, not the nonce.** The
  attacker model improves: an attacker reading `~/.shell/helper/shellx`
  now sees a 64-char hex digest, not the raw nonce. They must crack
  scrypt to recover the preimage (same as before, but with the
  profile-guessing shortcut eliminated).

### Security

- No change to scrypt cost (`N=2^15`, `r=8`, `p=1`) or cipher choice
  (ChaCha20 + HMAC-BLAKE2b). Only the `STATIC_PW` derivation changed.

### Fixed

- `executable_shellx_completion_helper` `main()` body was accidentally
  truncated in commit `c1701d0` (shellx 1.1.0, "derived slug, no
  marker"). The body has been restored from commit `1774519`.

## [1.3.0] — 2026-08-23

### Changed

- **`executable_shellx` is now a chezmoi template (`executable_shellx.tmpl`)**.
  Profile and nonce are rendered into the deployed script at `chezmoi apply`
  time, so runtime resolution is a constant-string read instead of a
  `chezmoi data` subprocess. This restores `runpriv`-class startup latency
  (cold start dropped from ~1.5–2.0 s to ~50–200 ms on a source tree that
  contains a 4 GB `.tmp/references/repository/kilocode/node_modules`
  clone). The deployed filename is unchanged: chezmoi strips `.tmpl` at
  apply time, so the binary still deploys as `~/.shell/helper/shellx`.

- **Runtime fallback chain added in `_load_env()`** so the script still
  works when invoked outside the chezmoi-deployed `$PATH` (CI, headless
  boxes, manual copy). Order: `SHELLX_PROFILE` / `SHELLX_NONCE` env vars
  → template-injected constants → `chezmoi data` subprocess. The slow
  path is exercised only by test/CI use; the normal deployed path is
  zero-subprocess.

### Migration from 1.2.x

- **Re-run `chezmoi apply`** so the deployed script is regenerated with
  the new template-rendered constants. No data migration needed — the
  on-disk blob format and the derived-slug store path are unchanged.
- **No API change.** All subcommands behave identically; only the cold
  startup time changes.

### Fixed

- (none)

### Security

- No change to the threat model. The deployed script still derives
  `STATIC_PW` from `chezmoi:shellx:<profile>:<nonce>`; only the source
  of `<profile>` and `<nonce>` changed (template instead of subprocess).
- See [`CRYPTO.md`](./CRYPTO.md) for the updated derivation rationale.

## [1.2.1] — 2026-08-17

### Fixed

- `shellx store` and the exec path (`shellx -- …`) crashed with a raw
  `UnicodeDecodeError` traceback when the secret value (or the bytes
  piped into stdin) contained non-UTF-8 data. `cmd_store` now reads
  stdin in binary mode (`sys.stdin.buffer.read()`) and decodes with
  `errors="surrogateescape"`; the matching `encode()` round-trips any
  byte losslessly. `cmd_exec` decodes decrypted plaintext with the
  same codec before assigning to `os.environ`. ASCII secrets behave
  identically; binary secrets store and inject end-to-end without
  crashing. (`dot_shell/helper/executable_shellx` — `cmd_store`,
  `cmd_exec`.)

## [1.2.0] — 2026-07-27

### Changed

- **Default export destination renamed**: `shellx export` now writes to
  `<source>/.encrypted_data/env_store/` (was `.encrypted_data/tokens/`).
  The new name better reflects that the directory holds general
  environment-variable exports — not just OAuth-style tokens. The wire
  format, JSONC schema, and import path detection are unchanged.
- `.chezmoiignore` updated to match: excludes
  `.encrypted_data/env_store/shellx*` from `chezmoi apply`.

### Fixed

- `shellx export` (with no `--to`) crashed with `ValueError: stdout and
  stderr arguments may not be used with capture_output` because
  `_detect_export_dir` set both `capture_output=True` and
  `stderr=subprocess.DEVNULL`. Switched to `stdout=subprocess.PIPE`,
  which is compatible with the explicit stderr redirect.

### Migration from 1.1

- **Existing exports need to be moved**:
  `git mv .encrypted_data/tokens .encrypted_data/env_store` (or just
  re-run `shellx export` after the upgrade — old files at the old path
  are still importable by passing an explicit path).
- **No data loss**: `shellx import` accepts any `.jsonc.age` file by
  path; only the *default* destination changed.
- The empty `.gitkeep` and `README.md` have been relocated from
  `tokens/` to `env_store/`. If you had your own files there, move them
  too.

## [1.1.0] — 2026-07-26

### Changed

- **Store slug is now derived from `STATIC_PW`** (32 hex chars; `blake2b` of
  the per-profile password, 16 bytes). The store directory is
  `~/.local/share/<slug>/` — reproducible across machines sharing the same
  chezmoi profile + nonce. No marker file is needed.
- The `~/.shellx-store` marker file is **no longer read or written**.
- `shellx init` no longer generates a random slug. The slug is fully
  determined by the current chezmoi config.
- `shellx` with no arguments no longer auto-initializes the store; it just
  prints help. Explicit `shellx init` is required.
- The `shellx init --slug-dir` flag has been removed. The store path is no
  longer user-configurable.

### Deprecated

- (none)

### Removed

- `~/.shellx-store` marker file (no longer consulted).
- `shellx init --slug-dir` flag.

### Fixed

- (none)

### Security

- No change to the threat model. The new slug is computable by anyone who
  knows the chezmoi profile + nonce — both of which were already present
  in the user's chezmoi config and exports. See [`LIMITATIONS.md`](./LIMITATIONS.md)
  for the "Slug predictability" section.

### Migration from 1.0

- **Existing stores continue to work.** The `.sl` file inside the store
  directory records the original (1.0) random slug, and `shellx` honors
  it when looking up blobs. To migrate to the derived slug, delete the
  store and re-run `shellx init` (you will lose existing entries; export
  + re-import if you need to preserve them).
- **Delete the obsolete marker file**: `rm ~/.shellx-store`. It is no
  longer consulted and harmless to leave in place, but cleaning it up
  removes a stale fingerprint.

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
- Random 16-hex slug directory under `~/.local/share/`. (Replaced in 1.1.0 by a slug derived from `STATIC_PW`; legacy stores with a `.sl` file continue to work.)
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