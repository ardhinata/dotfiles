---
name: ssh
description: SSH key handling on this host. Load before creating an SSH keypair, adding or selecting a key for the agent, changing which keys the agent exposes, checking which identity is loaded, reading anything under ~/.ssh/, or running a streaming command over ssh. Covers the gpg-agent as the SSH agent, the Use-for-ssh attribute, key lifetimes, and live remote output.
---

# SSH

This host keeps all SSH credentials in `gpg-agent --enable-ssh-support`. The
OpenSSH `ssh-agent` holds nothing.

## When to load

- About to create an SSH keypair: a deploy key, a work identity, or a
  one-off alias.
- About to add a key to the agent, or to change which keys the agent exposes.
- The user asks which key is loaded, what the fingerprint is, or whether a
  key is in the agent.
- About to read, list, or grep anything under `~/.ssh/`.
- About to run a command over `ssh` where live, line-by-line output matters.

## Where new keys go

`~/.ssh/agent-keys/` is the only `~/.ssh/` subdirectory the agent may create
or inspect. Keep new keys out of `~/.ssh/` itself: those paths belong to the
user's identity keys.

```bash
mkdir -p ~/.ssh/agent-keys && chmod 700 ~/.ssh/agent-keys
ssh-keygen -t ed25519 -f ~/.ssh/agent-keys/<service>-YYYY-MM -C "<comment>"
chmod 600 ~/.ssh/agent-keys/<name>          # private key
chmod 644 ~/.ssh/agent-keys/<name>.pub      # public key
ssh-add ~/.ssh/agent-keys/<name>
ssh-keygen -lf ~/.ssh/agent-keys/<name>.pub # fingerprint
```

Confirm the user wants a new key, and that no existing key fits the purpose.
Never overwrite an existing key. Ask first, even when the user says "make me
a key". Report the absolute path and the fingerprint together.

## The agent is gpg-agent

`SSH_AUTH_SOCK` points at the gpg-agent socket, here
`/run/user/1000/gnupg/S.gpg-agent.ssh`. "The agent" means gpg-agent.
"Load a key" means `ssh-add` against that socket, with no flag change.

Ask the agent about a usable identity. Never read the key file to find out:

| Question | Command |
|---|---|
| Which keys are loaded | `ssh-add -l` |
| Keygrips and auth subkeys | `gpg --list-keys --with-keygrip` |
| The agent socket path | `gpgconf --list-dirs agent-ssh-socket` |

Smartcard keys are added implicitly. Do not list them.

## Key selection

`~/.gnupg/sshcontrol` decides which keys the agent exposes to the SSH
protocol. The file is deprecated for that purpose since GnuPG 2.3.7. Set the
`Use-for-ssh` attribute on the key file instead:

```bash
gpg -k --with-keygrip                                    # find the auth subkey's keygrip
gpg-connect-agent 'keyattr <keygrip> Use-for-ssh: true' /bye
gpg-connect-agent updatestartuptty /bye                  # pinentry and agent reload
```

Remove it the same way with `Use-for-ssh: false`. Edit `sshcontrol` only when
you must support a client older than 2.3.7.

## Key lifetime

`ssh-add -t <seconds>` sets a per-key lifetime. The GnuPG 2.4.9 manual says a
non-zero TTL in `sshcontrol` overrides the global default set by
`--default-cache-ttl-ssh`. On this host the default is 7200 seconds and the
maximum is 86400.

Do not set a TTL and assume the key expires at that moment. A key in the
agent cache can be re-read from the private key store, so the practical
effect is on the agent cache, not on the key.

## Reading keys safely

Only these paths may be read:

- `~/.ssh/config`
- `~/.ssh/config.d/`
- `~/.ssh/agent-keys/` — directory listings and `*.pub` files only

Everything else under `~/.ssh/` is secret: `authorized_keys`, `known_hosts`,
private keys (`id_*`, `*.pem`, `keys/`), their `.pub` siblings, agent sockets,
and CA files. A secret path stays secret even when the matching key sits in
the agent. Read one only when the user opens it for this task.

## Live output over ssh

Without a pty the remote stdout is a pipe, so libc-style programs
block-buffer and print only at exit.

| Case | Fix |
|---|---|
| Dynamically linked command | `ssh host 'stdbuf -oL -eL ./build.sh'` |
| Python | `ssh host 'python -u script.py'` or `PYTHONUNBUFFERED=1`. `stdbuf` does not affect Python |
| Static binary, no `stdbuf` on the remote, or any other case | `ssh -tt host './build.sh'` |

`stdbuf` works through `LD_PRELOAD`, so it has no effect on a statically
linked binary. `ssh -tt` forces a tty, which merges stderr into stdout and
turns `\n` into `\r\n`. A remote that does not allocate a tty needs the
command wrapped, not the local `ssh`.

Do not reach for `nohup`, `&`, or `disown` to fix buffering. The problem is
the pipe, not job control. Use the harness background facility.
