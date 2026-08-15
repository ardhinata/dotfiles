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

## Anti-patterns

- Treating any key file's contents as low-sensitivity because the filename looks innocuous (e.g. `id_ed25519.pub` is harmless; the matching `id_ed25519` is not).
- Including key material in responses, logs, commits, or commit messages — even one line.
- Reading `~/.ssh/` directory listings as a "harmless first step" before deciding what to read.
- Asking the user to paste a key into chat "for convenience".

## References

- `~/.config/kilo/rules.personal.d/ssh-agent-keys-location.md` — where to put keys the agent generates.
