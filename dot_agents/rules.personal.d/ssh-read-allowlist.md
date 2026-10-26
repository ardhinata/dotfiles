# SSH Read Allowlist

Only `~/.ssh/config`, `~/.ssh/config.d/`, and `~/.ssh/agent-keys/` may be
read. Every other path under `~/.ssh/` is secret, including
`authorized_keys`, `known_hosts`, private keys (`id_*`, `*.pem`, `keys/`),
their `.pub` siblings, agent sockets, and CA files. A secret path stays
secret even when the matching key sits in the agent. Read, list, or grep one
only when the user opens it for this task.

Under `~/.ssh/agent-keys/`, directory listings and `*.pub` files are allowed.
Private keys are not.

SSH credentials live in gpg-agent. Ask the agent, never the key file, about a
usable SSH identity: `ssh-add -l` for fingerprints, `gpg --list-keys
--with-keygrip` for keygrips, and `gpgconf --list-dirs agent-ssh-socket` for
the socket path.

Do not list `~/.ssh/` as a first step before deciding what to read.
