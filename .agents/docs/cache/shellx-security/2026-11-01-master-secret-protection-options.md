---
source: kernel docs, man7 keyrings(7), Cloudflare key retention blog, LWN libsecret, ArchWiki gnome-keyring, local tests
captured: 2026-11-01
freshness: stable
tags: [shellx, secrets, keyring, libsecret, chezmoi]
---

# Protecting the shellx master secret

What the options are, what each one costs, and what this host actually
supports. Measured on 2026-11-01.

## The threat model

shellx exists to hide a secret from two readers: a file scanner that looks
for the token on disk, and an infostealer that reads a running process. It
does not aim at maximum cryptographic strength. That changes the ranking of
the options below, because the master secret is only interesting to an
attacker who can read the helper.

## The current state

| Item | Mode | Holds |
|---|---|---|
| `~/.shell/helper/shellx` | 0755 | `SHELLX_NONCE_DEFAULT` and `SHELLX_STATIC_PW_DEFAULT` as plain literals |
| `~/.shell/helper/__pycache__/shellxcpython-314.pyc` | 0644 | The same two literals, a second copy |
| `~/.local/share/<slug>/` | 0700 | The store directory |
| `~/.local/share/<slug>/<blob>` | 0600 | The encrypted blobs |

The master secret is `sha256("com.ardju.utils:shellx:" + nonce)`. The nonce
is 64 random alphanumeric characters from `randAlphaNum 64`, so it holds at
least 341 bits of entropy. The `0600` and `0700` modes are therefore not
doing much work: the key sits next to the lock in a world-readable file.

## Option 1 — Separate the master secret into its own file

Move the literal into a `0600` file and read it at runtime.

| Property | Value |
|---|---|
| On disk | Yes, in a `0600` file |
| A file scanner finds the token | No |
| A local user reads it | No |
| Bootstrap | None |
| Read cost | 0.6 ms |

This is the minimum change and it removes the secret from the helper, from
the `.pyc`, and from the repo. It does not remove it from the disk.

## Option 2 — The Linux kernel keyring

The kernel keeps key payloads in RAM. Nothing is written to a disk.

| Property | Value |
|---|---|
| On disk | No |
| A file scanner finds the token | No |
| A local user reads it | Yes, if they can run `keyctl` as the same user |
| Bootstrap | The secret has to arrive from somewhere once |
| Read cost | 2.5 ms for `keyctl request` plus `keyctl pipe` |

The commands, verified on this host:

```sh
keyctl padd user shellx-master @u      # reads the payload from stdin
keyctl request user shellx-master       # prints the key serial
keyctl pipe <serial>                    # prints the payload
```

The user keyring `@u` survives logout and login and lives in RAM only until
the next reboot. The session keyring `@s` is inherited by every child process
and is dropped at logout. A reboot therefore loses the secret, so the store
needs a recovery path.

## Option 3 — libsecret through `secret-tool`

The secret moves into the Secret Service provider. The provider stores it
encrypted, and the unlock state belongs to the login session.

| Property | Value |
|---|---|
| On disk | Only inside the provider's encrypted store |
| A file scanner finds the token | No |
| A local user reads it | Only while the provider is unlocked |
| Bootstrap | The provider has to be running and unlocked |
| Read cost | 7.6 ms per lookup |

This host runs the KDE provider. `busctl --user list` shows
`org.freedesktop.secrets` owned by `ksecretd`. The round trip works:

```sh
secret-tool store --label=shellx service shellx key master
secret-tool lookup service shellx key master
secret-tool clear service shellx key master
```

The dependency is the provider. Without it, the helper has no key and the
shell startup fails.

## Option 4 — systemd-creds

`systemd-creds` is installed and can encrypt a credential with the host key
or the TPM.

Rejected for this use. The host key lives in
`/var/lib/systemd/credentials/host.key` and is root-only, so an
unprivileged helper cannot decrypt it. The TPM mode needs the TPM storage
root key, which the kernel does not expose to an unprivileged process. Both
modes work for a systemd service, not for a helper that a shell runs.

## Option 5 — An interactive unlock

The helper asks for a passphrase at shell startup.

Rejected. It adds a prompt to every new shell, which breaks the
non-interactive path and stops the shell from starting at all when the
prompt is missed.

## The chezmoi mode attributes

Verified in a scratch HOME on 2026-11-01.

| Source name | Target mode |
|---|---|
| `executable_dot_x` | 0755 |
| `private_dot_x` | 0600 |
| `private_executable_dot_x` | 0700 |

`private_executable_` is the one to use for a helper that must hold a
secret. The combination is not documented in the attribute table, but chezmoi
applies both attributes.

## Recommendation

Use option 1 as the base and option 2 as the runtime layer. The secret
lives in a `0600` file, the helper is `0700`, and the helper pushes the
secret into the user keyring at startup. A file scanner never sees the
secret. A local user can still read it through the keyring, but so can they
read the `0600` file, so the keyring adds no new exposure while it removes
the secret from the file.

Option 3 is the better answer when the provider is always present. It costs
7.6 ms per lookup, and the helper must fail open or fail closed when the
provider is locked. That failure mode is a correctness decision, not a
performance one.

## Source

- [Kernel Key Retention Service](https://docs.kernel.org/security/keys/core.html)
- [keyrings(7)](https://man7.org/linux/man-pages/man7/keyrings.7.html)
- [The Linux Kernel Key Retention Service and why you should use it](https://blog.cloudflare.com/the-linux-kernel-key-retention-service-and-why-you-should-use-it-in-your-next-application/)
- [Libsecret revealed](https://lwn.net/Articles/490518/)
- [GNOME/Keyring](https://wiki.archlinux.org/title/GNOME/Keyring)

## Freshness note

The kernel keyring and the libsecret API are stable. `secret-tool` has kept
its command shape since 2012. Re-verify the provider name on this host before
relying on option 3, because the desktop environment can change it.

## See also

- [Shellx helper optimization plan](../../../../docs/plans/2026-11-01-shellx-helper-optimization.md)
- [Agent permission and safety-net issues](../../../../docs/reports/2026-11-01-agent-permission-and-safety-net-issues.md)
