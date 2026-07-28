# Install

`shellx` is part of this chezmoi dotfiles repo. Once the repo is applied,
no separate install step is needed. The `shellx` binary lives at
`~/.shell/helper/shellx` after `chezmoi apply`.

## Requirements

| Component | Version | Notes |
|---|---|---|
| Python 3 | ≥ 3.10 | `hashlib.scrypt`, `secrets`, `hashlib.blake2b` (passed to `hmac.new`) required. Available on every modern Linux distro Python. Uses PEP 604 `str | None` and PEP 585 built-in generics. |
| `age` | any recent | Needed transitively via `chezmoi encrypt` (export) and `chezmoi decrypt` (import). Not needed for runtime secret injection. |
| `chezmoi` | ≥ 2.70.4 | Needed for `export` and `import` subcommands. |
| POSIX shell | — | Used to invoke `shellx` from `~/.shell/zsh/10-common-export.zsh`. |

If you only need runtime injection (`shellx --tag=… -- proc …`), you only
need Python 3 — no `age` or `chezmoi` at invocation time.

## Onboarding

After the first `chezmoi apply`:

```bash
# 1. Verify shellx is on PATH.
which shellx        # → /home/<you>/.shell/helper/shellx

# 2. Run init.
shellx init

# 3. Confirm the store was created.
ls -la ~/.local/share/
```

Output of step 3 will show a single `<64-hex-chars>/` directory. The name
is `blake2b("chezmoi:shellx:<profile>:<nonce>")[:16].hex()` — deterministic
from your chezmoi config, so the same profile + nonce on another machine
will resolve to the same path. No marker file is needed.

## First secret

```bash
# Stdin mode (preferred for piping from another tool):
printf 'ghp_xxxxxxxxxxxxxxxxxxxx' | shellx store GH_TOKEN --tag=git,api --process=gh,glab

# TTY mode (interactive prompt, no echo):
shellx store GH_TOKEN --tag=git,api --process=gh,glab
# Enter value for GH_TOKEN: ********
```

Either way the secret is encrypted with the per-profile `STATIC_PW` and
written to `~/.local/share/<slug>/<blake2b-hash>`. The index file `.idx`
is updated with the tag/process routing.

## Try it

```bash
# Inject GH_TOKEN into `gh pr list`:
shellx --tag=git gh pr list

# Inject all secrets whose `process` list contains `npm`:
shellx -- npm whoami

# Inspect the injected var list:
shellx --tag=git env | grep '^RUNPRIV_VARS='
# → RUNPRIV_VARS=GH_TOKEN
```

## Zsh completion

Completion is auto-installed via the `#compdef shellx` autoload tag and
`$SHELL_TOOL_DIR/zsh/completions` being on `fpath`. If it does not load:

```bash
# Force compinit rebuild:
rm -f ~/.zcompdump; exec zsh

# Verify:
shellx <TAB>          # → init, store, list, rm, export, import
shellx store <TAB>    # → existing var names
shellx --tag=<TAB>    # → known tags
```

If completion is silent (no candidates), the store is uninitialized —
run `shellx init` once.

## CI / headless use

`shellx init` is interactive only by default (it just prints, no prompt).
For headless first-time setup on a CI box where you already know the
profile and nonce, compute the derived slug and create the directory by
hand:

```bash
# Compute the derived slug for the current profile + nonce.
SLUG=$(python3 -c 'import hashlib; print(hashlib.blake2b(b"chezmoi:shellx:<profile>:<nonce>", digest_size=16).hexdigest())')

mkdir -p ~/.local/share/"$SLUG"
chmod 700 ~/.local/share/"$SLUG"
printf '%s\n' "$SLUG" > ~/.local/share/"$SLUG"/.sl
chmod 600 ~/.local/share/"$SLUG"/.sl
: > ~/.local/share/"$SLUG"/.idx
chmod 600 ~/.local/share/"$SLUG"/.idx
```

Then `shellx import <path>` to populate from an existing export.

## Uninstall / reset

To wipe a store and start fresh:

```bash
SLUG=$(python3 -c 'import hashlib; print(hashlib.blake2b(b"chezmoi:shellx:<profile>:<nonce>", digest_size=16).hexdigest())')
rm -rf "$HOME/.local/share/$SLUG"
shellx init    # recreates the derived-slug store
```

This does **not** affect chezmoi source tree (exports live in
`.encrypted_data/env_store/` and must be removed separately if desired).