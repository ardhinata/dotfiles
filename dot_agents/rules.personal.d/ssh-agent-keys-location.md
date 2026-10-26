# SSH Key Placement

New SSH keys go under `~/.ssh/agent-keys/`. That is the only `~/.ssh/`
subdirectory the agent may create or inspect. Keep new keys out of `~/.ssh/`
itself: those paths belong to the user's identity keys.

Never overwrite an existing key. Ask first, even when the user says "make me
a key".

All SSH credentials live in `gpg-agent --enable-ssh-support`, not OpenSSH
`ssh-agent`. "The agent" means gpg-agent. Smartcard keys are added
implicitly, so do not list them.

Ask the agent about a usable identity, never the key file: `ssh-add -l` for
fingerprints, `gpg --list-keys --with-keygrip` for keygrips, and
`gpgconf --list-dirs agent-ssh-socket` for the socket path.

Load the `ssh` skill for the key creation procedure, key selection, key
lifetimes, and live output over ssh.
