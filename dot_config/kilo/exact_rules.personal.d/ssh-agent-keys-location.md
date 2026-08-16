When the agent generates a new SSH key on the user's behalf, place it under `~/.ssh/kilo-keys/` — the only `~/.ssh/` subdirectory the agent is allowed to create and inspect.

## SSH agent is gpg-agent

All SSH credentials in this environment live in **`gpg-agent --enable-ssh-support`**, not OpenSSH `ssh-agent`. `SSH_AUTH_SOCK` is set to `$(gpgconf --list-dirs agent-ssh-socket)` (see `dot_shell/zsh/12-gpg.zsh`). Keys are encrypted at rest under `~/.gnupg/private-keys-v1.d/` and listed in `~/.gnupg/sshcontrol` by keygrip. Smartcard keys are added implicitly — do not list them.

When this doc says "the agent", it means gpg-agent. When it says "load a key", it means `ssh-add` against the gpg-agent socket (no flag change).

## When

About to create a new SSH keypair (deploy key, work-specific identity, one-off alias, etc.).

## Process

1. Confirm the user wants a new key, and that no existing key fits the purpose.
2. `mkdir -p ~/.ssh/kilo-keys && chmod 700 ~/.ssh/kilo-keys`.
3. Generate the keypair: `ssh-keygen -t ed25519 -f ~/.ssh/kilo-keys/<service>-YYYY-MM -C "<comment>"` (descriptive filename, year-month tag).
4. `chmod 600` on the private key, `chmod 644` on the `.pub` sibling.
5. `ssh-add ~/.ssh/kilo-keys/<name>`, then tell the user the absolute path and fingerprint (`ssh-keygen -lf <path>`).

## Per-key lifetime — `ssh-add -t` is **NOT** honored by gpg-agent

**Important finding:** gpg-agent implements the OpenSSH agent protocol but **silently ignores the per-key lifetime** that `ssh-add -t <life>` sends. The `-t` flag appears to succeed (no error), but the key caches for the global `default-cache-ttl-ssh` / `max-cache-ttl-ssh` instead.

To set a per-key TTL, edit `~/.gnupg/sshcontrol` after `ssh-add` has written the keygrip:

```
# Format: <40-hex-keygrip> <ttl-seconds|0=default> [flags]
ABCDEF...1234 3600
```

Then restart the agent: `gpgconf --kill gpg-agent` (auto-respawns). Smartcard keys cannot have per-key TTLs.

**Decision rule:** if the user wants a per-key TTL, do **not** pass `-t` to `ssh-add` and assume it worked. Edit `sshcontrol` and restart.

## Anti-patterns

- Overwriting an existing key silently — always ask first, even when the user says "make me a key".
- Putting keys directly under `~/.ssh/` (e.g. `~/.ssh/id_ed25519`) — those collide with the user's identity keys.
- Reading existing key contents to "see what we already have" before generating — see `ssh-read-allowlist.md`.
- Returning a key fingerprint to the user without telling them the path (or vice versa).
- Adding `ssh-add -t 1h` and assuming the key expires in 1 h — gpg-agent ignores it. Documented above.
- Editing `sshcontrol` and assuming the new TTL applies immediately — it does not; the agent must be restarted.
