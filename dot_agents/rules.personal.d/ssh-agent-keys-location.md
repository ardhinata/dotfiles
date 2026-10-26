# SSH Key Placement

New SSH keys go under `~/.ssh/agent-keys/`. That is the only `~/.ssh/`
subdirectory the agent may create or inspect.

## When

About to create a new SSH keypair: a deploy key, a work identity, or a
one-off alias.

## Process

1. Confirm the user wants a new key, and that no existing key fits.
2. `mkdir -p ~/.ssh/agent-keys && chmod 700 ~/.ssh/agent-keys`.
3. `ssh-keygen -t ed25519 -f ~/.ssh/agent-keys/<service>-YYYY-MM -C "<comment>"`.
4. `chmod 600` on the private key, `chmod 644` on the `.pub` sibling.
5. `ssh-add ~/.ssh/agent-keys/<name>`, then report the absolute path and the
   fingerprint (`ssh-keygen -lf <path>`).

Never overwrite an existing key. Ask first, even when the user says "make me
a key". Keep new keys out of `~/.ssh/` itself: those paths belong to the
user's identity keys.

## The agent is gpg-agent

All SSH credentials live in `gpg-agent --enable-ssh-support`, not OpenSSH
`ssh-agent`. `SSH_AUTH_SOCK` points at the gpg-agent socket. "The agent"
means gpg-agent. Smartcard keys are added implicitly, so do not list them.

## Key selection and lifetime

- `ssh-add -t <seconds>` sets a per-key lifetime. A non-zero TTL overrides
  `--default-cache-ttl-ssh`, which is 7200 seconds on this host with a
  maximum of 86400.
- Do not edit `~/.gnupg/sshcontrol` to choose which keys are exposed. The
  file is deprecated for that purpose since GnuPG 2.3.7. Set the attribute
  instead:

```bash
gpg -k --with-keygrip                                    # find the auth subkey's keygrip
gpg-connect-agent 'keyattr <keygrip> Use-for-ssh: true' /bye
gpg-connect-agent updatestartuptty /bye                  # pinentry and agent reload
```
