When the agent generates a new SSH key on the user's behalf, place it under `~/.ssh/kilo-keys/` — the only `~/.ssh/` subdirectory the agent is allowed to create and inspect.

## SSH agent is gpg-agent

All SSH credentials in this environment live in **`gpg-agent --enable-ssh-support`**, not OpenSSH `ssh-agent`. `SSH_AUTH_SOCK` is set to `$(gpgconf --list-dirs agent-ssh-socket)` (see `dot_shell/zsh/12-gpg.zsh`). Keys are encrypted at rest under `~/.gnupg/private-keys-v1.d/` and listed in `~/.gnupg/sshcontrol` by keygrip. Smartcard keys are added implicitly — do not list them.

When this doc says "the agent", it means gpg-agent. When it says "load a key", it means `ssh-add` against the gpg-agent socket (no flag change).

## When

About to create a new SSH keypair (deploy key, work-specific identity, one-off alias, etc.).

## Process

1. Confirm the user wants a new key, and that no existing key fits the purpose.
2. Create the directory if missing:
   ```bash
   mkdir -p ~/.ssh/kilo-keys && chmod 700 ~/.ssh/kilo-keys
   ```
3. Generate the keypair into that directory (e.g. `ssh-keygen -t ed25519 -f ~/.ssh/kilo-keys/<descriptive-name> -C "<comment>"`).
4. Set permissions:
   - `chmod 700` on the directory (already done in step 2).
   - `chmod 600` on private keys.
   - `chmod 644` on `.pub` siblings.
5. Tell the user the **absolute path** of the new key and its **fingerprint** (`ssh-keygen -lf <path>`).

## Naming

Pick a descriptive filename that includes:

- The platform or service (e.g. `github-work`, `gitlab-prod-deploy`).
- A short year-month tag (e.g. `-2026-07`) so concurrent keys don't collide.

Example: `github-work-2026-07`.

## Loading the key into the agent

```bash
ssh-add ~/.ssh/kilo-keys/<descriptive-name>
```

After this, the key is held by gpg-agent; the on-disk file becomes optional for ongoing use (see `ssh-read-allowlist.md`).

## Per-key lifetime — `ssh-add -t` is **NOT** honored by gpg-agent

**Important finding (verified against gpg-agent docs and user reports):** gpg-agent implements the OpenSSH agent protocol but **silently ignores the per-key lifetime** that `ssh-add -t <life>` sends. The `-t` flag appears to succeed (no error), but the key caches for the global `default-cache-ttl-ssh` / `max-cache-ttl-ssh` instead. See:

- `gpg-agent(1)`: "An entry starts with optional whitespace, followed by the keygrip of the key given as 40 hex digits, **optionally followed by the caching TTL in seconds** and another optional field for arbitrary flags. A non-zero TTL overrides the global default as set by `--default-cache-ttl-ssh`."
- pyratelog.net (2023-03-09): "I started using gpg-agent for ssh I noticed that this setting was not observed for the ssh key... you can add a custom value after the keygrip in `~/.gnupg/sshcontrol`."
- gnupg-users 2010-10 / GnuPG bug T1240: closed 2009, "The TTL specified in sshcontrol for SSH keys is ignored" — recurring reports since.

To set a per-key TTL, edit `~/.gnupg/sshcontrol` **after** `ssh-add` has written the keygrip:

```
# Format: <40-hex-keygrip> <ttl-seconds|0=default> [flags]
ABCDEF...1234 3600
```

Then restart the agent: `gpgconf --kill gpg-agent` (it auto-respawns). The per-key TTL only takes effect after restart. Smartcard keys cannot have per-key TTLs.

**Decision rule:** if the user wants a per-key TTL, do **not** pass `-t` to `ssh-add` and assume it worked. Instead, edit `sshcontrol` and confirm with `gpgconf --list-options gpg-agent | grep cache-ttl-ssh` and by inspecting the file.

## Global agent lifetime knobs

If per-key TTLs are not needed, the global pair in `~/.gnupg/gpg-agent.conf` controls everything:

```conf
default-cache-ttl-ssh 1800   # 30 min idle eviction
max-cache-ttl-ssh     7200   # 2 h hard ceiling
```

These **are** honored and are the only `-t`-equivalent controls that gpg-agent respects. Do not propose adding `-t` to `ssh-add` as if it were sufficient — it isn't.

## Anti-patterns

- Overwriting an existing key silently — always ask first, even when the user says "make me a key".
- Putting keys directly under `~/.ssh/` (e.g. `~/.ssh/id_ed25519`) — those collide with the user's identity keys.
- Reading existing key contents to "see what we already have" before generating — see `ssh-read-allowlist.md`.
- Returning a key fingerprint to the user without telling them the path (or vice versa).
- Adding `ssh-add -t 1h` and assuming the key expires in 1 h — gpg-agent ignores it. Documented above.
- Editing `sshcontrol` and assuming the new TTL applies immediately — it does not; the agent must be restarted.

## References

- `~/.config/kilo/rules.personal.d/ssh-read-allowlist.md` — read constraints that motivate this location.
- `gpg-agent(1)` §"sshcontrol" — TTL syntax.
- `dot_shell/zsh/12-gpg.zsh` — wires `SSH_AUTH_SOCK` to gpg-agent and refreshes GPG_TTY.
- `dot_ssh/config` — `Match host * exec "gpg-connect-agent updatestartuptty /bye"` keeps the agent's TTY view current.
