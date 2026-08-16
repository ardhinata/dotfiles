Only `~/.ssh/config` and `~/.ssh/config.d/` may be read freely; every other path under `~/.ssh/` is treated as secret.

## When

About to read, list, grep, or otherwise inspect anything under `~/.ssh/`.

## Allowlist

The agent **may read/inspect** only:

- `~/.ssh/config`
- `~/.ssh/config.d/` (any file inside)

## Deny (unless the user explicitly opens them for this task)

Everything else under `~/.ssh/`, including but not limited to:

- `authorized_keys`, `authorized_keys.d/`
- `known_hosts`, `known_hosts.old`
- Private keys: `*.pem`, files inside `~/.ssh/keys/`, `id_rsa`, `id_ed25519`, `id_ecdsa`, `id_dsa`, `kilo-deploy-*`, and any other `id_*` shape.
- Their `.pub` siblings.
- Any other key material, agent sockets, control sockets, certificate authority files.

## Don't query the key file — ask the agent

All SSH credentials in this environment are loaded into **gpg-agent**. Once a key is loaded, the on-disk file is no longer the source of truth — gpg-agent holds the live key material encrypted at rest under `~/.gnupg/private-keys-v1.d/` and exposes operations over the agent socket.

When the user asks "which SSH key is loaded?", "what's the fingerprint?", "is this key in the agent?", or anything else about currently usable SSH identity — **ask the agent, not the file**: `ssh-add -l` (fingerprints), `gpg --list-keys --with-keygrip`, `gpgconf --list-dirs agent-ssh-socket` (only `.pub` siblings are safe for `ssh-keygen -lf`).

`~/.ssh/known_hosts` and private-key files are still secret even if the corresponding key is "in the agent" — the file path itself is enough to trigger the deny list.

## Anti-patterns

- Treating any key file's contents as low-sensitivity because the filename looks innocuous (e.g. `id_ed25519.pub` is harmless; the matching `id_ed25519` is not).
- Reading `~/.ssh/` directory listings as a "harmless first step" before deciding what to read.
- Reading a private key file to learn "what's loaded" when `ssh-add -l` would answer without touching disk.
