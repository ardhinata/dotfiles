---
source:
  - https://github.com/openssh/openssh-portable
captured: 2026-10-29
freshness: check-2027-04
tags: [ssh, openssh, gpg-agent]
---

# Public-key try order with a gpg-agent on this host

A host's own `IdentityFile` is tried last when the agent holds that key,
because the agent's list order wins over the config order.

Captured 2026-10-29. Verified live on this host against OpenSSH 10.6p1 and
the OpenSSH portable master branch.

## Finding

`ssh -G` reports the config order, but the live attempt order differs when a
gpg-agent holds the key. The agent decides, not the config. For a host
block that names `~/.ssh/keys/<work-key>.pem.pub`:

```
Will attempt key: .../default-2026.key.pub            ECDSA   ... explicit agent
Will attempt key: .../default-2018.key.pub            ED25519 ... explicit agent
Will attempt key: .../<work-key>.pem.pub               ED25519 ... explicit agent
```

`pubkey_prepare()` in `sshconnect2.c` builds the try list in two groups:

1. `agent_keys` — keys the **agent** holds AND that the config also lists.
   This group is ordered by the **agent's** key list, because the loop walks
   `idlist` (the agent's identity list) and moves each matching config entry
   into `agent_keys` in that order.
2. `files` — config-listed keys the agent does not hold. This group keeps the
   config order.

`agent_keys` is concatenated into the preferred list **before** `files`
(`TAILQ_CONCAT(preferred, &agent_keys, next)` then
`TAILQ_CONCAT(preferred, &files, next)`). For any key that lives in the agent,
the config order is irrelevant — the agent's order wins.

On this host the agent is gpg-agent. `ssh-add -l` shows its order, and the
work key sits at position 8, after both defaults.

## Evidence

**`IdentityFile none` does not reset the list.** `IdentityFile` adds rather
than overrides ("Multiple IdentityFile directives will add to the list of
identities tried (this behaviour differs from that of other configuration
directives)" — `ssh_config(5)`). In `ssh.c` the literal string `none` only
causes that one entry to be skipped while loading
(`strcasecmp(options.identity_files[i], "none") == 0`). It does not clear
entries added by an earlier matching block:

```
Host *            → IdentityFile a.pub
Host target       → IdentityFile none
                   → IdentityFile b.pub

$ ssh -G target | grep identityfile
identityfile a.pub
identityfile none
identityfile b.pub
```

`none` suppresses the built-in defaults (`~/.ssh/id_rsa` and friends) when no
other identity is listed. It is not a reset switch.

**What works, in order of preference.**

*Option A — exclude the host from the shared defaults block (recommended).*
Negating the host in the `Host` pattern of the catch-all block keeps the
default keys for every other host and removes them for that one:

```
# ~/.ssh/config.d/default-keys.general.conf
Host * !<work-host>
    IdentityFile ~/.ssh/keys/default-2026.key.pub
    IdentityFile ~/.ssh/keys/default-2018.key.pub
```

Measured result on the host above: one key offered, accepted on the first
try (`Authenticated to <host> (<host>:<port>) using "publickey"`). Other
hosts are unaffected — `ssh -G github.com` still lists both defaults. Cost:
that host loses the default-key fallback.

*Option B — `IdentityAgent none` plus the private key file.* The config order
is restored when the agent is out of the picture, but the private key file
must be named (not the `.pub`), and it is passphrase protected on this host:

```
Host <work-host>
    IdentityAgent none
    IdentityFile ~/.ssh/keys/<work-key>.pem
```

Result: correct order, but every connection prompts for the passphrase. With
`BatchMode` it fails outright (`read_passphrase: can't open /dev/tty`).

*Option C — a dedicated agent socket for that host.* `IdentityAgent` pointing
at a second agent that holds only the intended key gives the same clean order
with no prompt. The key is passphrase protected, so it must be `ssh-add`-ed to
that agent each session.

*Option D — reorder the agent's own list.* Not a supported knob. The order
comes from gpg-agent internals and there is no user-facing control.

**Debug recipe.**

```bash
ssh -G <host> | grep -i identityfile      # config order (additive, not try order)
ssh -v <host> true 2>&1 | grep 'Will attempt key'   # real order
ssh-add -l                                 # the agent's order (the deciding factor)
ssh -o IdentityAgent=none -v <host> true 2>&1 | grep 'Will attempt key'  # config order only
```

The last one is the clean A/B: it removes the agent from the picture and shows
the config order in isolation.

**Other notes.** A public-key file in `IdentityFile` is enough when the agent
holds the private half; without the agent the same `.pub` path yields
`Load key "....pub": invalid format`, because ssh looks for the private key at
the same path. The deployed private key here is `~/.ssh/keys/<work-key>.pem`
while the config names the `.pem.pub` file. A host block whose `Host` pattern
does not match the name you type is silently ignored, and only `Host *`
applies. A `none` entry in `ssh -G` output is a config artefact, not a key.

## Why it matters

A config that looks correct can still fail to use the intended key. The agent
is the deciding factor on this host, so the fix belongs in the `Host` pattern
of the shared defaults block.

## Scope

This host. OpenSSH 10.6p1 client with gpg-agent as the SSH agent. The
`pubkey_prepare()` group order is not covered by any compatibility promise.

## Uncertainty

Re-verify after an OpenSSH major upgrade. The upstream source was read at
master, not at the 10.6p1 tag, so a release branch may differ.

## Source

- `openssh/openssh-portable` master: `sshconnect2.c` (`pubkey_prepare`,
  `order_identities_by_prio`), `readconf.c` (`oIdentityFile`,
  `add_identity_file`), `ssh.c` (identity file load loop).
- `ssh_config(5)` on this host (OpenSSH 10.6p1).
- Live `ssh -G`, `ssh -v`, `ssh-add -l` runs on this host, 2026-10-29.

## See also

- `dot_agents/skills/ssh/SKILL.md` — the skill that carries this rule
