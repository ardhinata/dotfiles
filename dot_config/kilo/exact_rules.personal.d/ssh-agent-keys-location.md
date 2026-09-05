When the agent generates a new SSH key on the user's behalf, place it under `~/.ssh/kilo-keys/` — the only `~/.ssh/` subdirectory the agent is allowed to create and inspect.

## SSH agent is gpg-agent

All SSH credentials in this environment live in **`gpg-agent --enable-ssh-support`**, not OpenSSH `ssh-agent`. `SSH_AUTH_SOCK` is set to `$(gpgconf --list-dirs agent-ssh-socket)` (see `dot_shell/zsh/12-gpg.zsh`). Keys are encrypted at rest under `~/.gnupg/private-keys-v1.d/`. Smartcard keys are added implicitly — do not list them.

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

## `sshcontrol` is deprecated — use `Use-for-ssh` attribute

As of GnuPG 2.3.7 (announced 2022-08, verified live at `gnupg.org/documentation/manuals/gnupg/Agent-Configuration.html` and `gnupg.org/documentation/manuals/gnupg/Agent-Options.html`), `~/.gnupg/sshcontrol` is **deprecated in favor of the "Use-for-ssh" attribute in the key files**. The upstream source verbatim:

> sshcontrol ... This file is deprecated in favor of the "Use-for-ssh" attribute in the key files.

`gpg-agent` now decides which authentication subkeys to expose to SSH by inspecting the per-key `Use-for-ssh` attribute (set via `gpg-connect-agent`'s `keyattr` command) rather than reading `sshcontrol`. The presentation order is: negative `Use-for-ssh` first, then active smartcards, then positive `Use-for-ssh` in numeric order, then `sshcontrol` entries (deprecated, present for compatibility).

To add a GPG authentication subkey for SSH use:

```bash
gpg -k --with-keygrip                                    # find the auth subkey's keygrip
gpg-connect-agent 'keyattr <keygrip> Use-for-ssh: true' /bye
gpg-connect-agent updatestartuptty /bye                  # pinentry + agent reload
```

To remove it:

```bash
gpg-connect-agent 'keyattr <keygrip> Use-for-ssh: false' /bye
```

**Decision rule:** do not edit `~/.gnupg/sshcontrol` for new SSH setups. Use `Use-for-ssh` via `gpg-connect-agent`. Edit `sshcontrol` only if you must support a pre-2.3.7 client.

## Anti-patterns

- Overwriting an existing key silently — always ask first, even when the user says "make me a key".
- Putting keys directly under `~/.ssh/` (e.g. `~/.ssh/id_ed25519`) — those collide with the user's identity keys.
- Reading existing key contents to "see what we already have" before generating — see `ssh-read-allowlist.md`.
- Returning a key fingerprint to the user without telling them the path (or vice versa).
- Adding `ssh-add -t 1h` and assuming the key expires in 1 h — gpg-agent ignores it.
- Editing `~/.gnupg/sshcontrol` to control which GPG subkeys are exposed to SSH — deprecated since GnuPG 2.3.7; use `Use-for-ssh` via `gpg-connect-agent`.
- Setting a per-key TTL by editing `sshcontrol`'s `<keygrip> <ttl>` column — that TTL field is also deprecated; per-key caching now lives in the global `default-cache-ttl-ssh` / `max-cache-ttl-ssh` knobs (`~/.gnupg/gpg-agent.conf`).
