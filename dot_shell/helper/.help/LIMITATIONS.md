# Limitations

`shellx` is **defense in depth**, not a vault. This document is an
honest list of what it does and does not defend against.

## What shellx defends against

- ✅ **Static home-directory scans** by signature-based infostealers that
  look for `token|secret|cred|key|password` in filenames or content.
- ✅ **Plaintext tokens in shell history** (you never type them; values
  come from stdin or interactive prompt only).
- ✅ **Plaintext tokens in `~/.bash_history` / `~/.zsh_history`** (same
  reason — `shellx store` reads the value via stdin, not argv).
- ✅ **Plaintext tokens in persistent env** (no `export VAR=value`).
- ✅ **Plaintext tokens in shell rc files** (no rc writes).
- ✅ **Plaintext tokens in well-known config paths** (`~/.aws/credentials`,
  `~/.netrc`, `~/.npmrc`, `~/.config/gh/hosts.yml`) — they live only in
  the derived-slug store.
- ✅ **Offline brute force of the on-disk ciphertext** (scrypt 2¹⁵/8/1
  ≈ 32 MiB per attempt).
- ✅ **Blob-swap attacks** (AAD binds ciphertext to its variable name).

## What shellx does NOT defend against

### `/proc/<pid>/environ` of the launched child

When `shellx --tag=git gh pr list` runs, the `gh` process inherits the
`GH_TOKEN` env var. Any process with read access to `/proc/<gh-pid>/environ`
can see it. This is **fundamental to how Unix environment variables
work** and there is no portable way to inject secrets into a child
without going through its environment.

**Mitigations:**
- Run sensitive commands from short-lived shells.
- Use a dedicated user account for high-value tokens (e.g.,
  `sudo -u tokens-user gh …`).
- Restrict `/proc` access via `hidepid=2` mount option on `/proc` (root
  required).

### Live memory dump of the child process

A debugger, kernel module, or root-level attacker can `ptrace` or
`/proc/<pid>/mem` the child and read the secret from its heap. This is
true of **any** secret-handling tool on Linux that does not use a
hardware enclave (SGX, TrustZone, etc.) — `shellx` is no exception.

### Live memory dump of `shellx` itself

`shellx` does its best to scrub plaintext buffers with `b"\x00" * len`,
but Python's GC may have copied the bytes to internal buffers (string
interning, etc.) that we cannot reliably overwrite. CPython also does
not provide `mlock(2)` in the stdlib.

**Implication:** while `shellx` is decrypting a blob (a few hundred ms),
the plaintext briefly exists in the process heap. A concurrent attacker
with `/proc/<shellx-pid>/mem` access could read it.

### Malware already inside the child process

If the launched binary itself is malicious or compromised, it can read
its own env and exfiltrate. `shellx` cannot distinguish a legitimate
`gh` from a `gh` trojan.

**Mitigations:** verify binary integrity (cosign, sigstore, distro
package manager GPG signatures); use a dedicated user for sensitive
workflows.

### Root-level attacker

Root can read any file (`~/.local/share/<slug>/*`), trace any syscall,
and modify any process. There is no mitigation at the user level — use
full-disk encryption (LUKS, FileVault) and a screen lock.

### Age key compromise

Exports are encrypted to age recipients in `.encryption_keys/`. If an
attacker obtains your private age key, they can decrypt any export and
import it onto another machine.

**Mitigations:** rotate keys periodically, never commit `*.secret.key`,
back up only to encrypted offline storage.

### Profile-name leakage (resolved in 1.5.0)

In shellx 1.4.x and earlier, `STATIC_PW` mixed a guessable `<profile>`
component with the random `<nonce>`:

```text
# 1.4.x derivation
STATIC_PW = "chezmoi:shellx:<profile>:<nonce>"
```

If `<profile>` was guessable (e.g., `personal-laptop`) and an attacker
had a ciphertext, they could try candidate profiles — each candidate
requiring a full scrypt derivation (~100 ms, ~32 MiB) to test, so
online guessing was impractical and offline brute force was bounded by
profile-name entropy.

As of **shellx 1.5.0**, `STATIC_PW` is a SHA-256 hash of
`"com.ardju.utils:shellx:" + <nonce>` — profile is no longer part of
the derivation at all. The deployed script embeds the 64-char hex
digest; the nonce itself is not visible in `~/.shell/helper/shellx`.
The attacker must crack scrypt to recover the preimage.

### Cross-tool keyspace collision

As of shellx 1.5.0, the shared `system_environment.nonce` is intended
for reuse by other tools. Each tool that needs a derivation must pick
its own `com.ardju.utils:<tool>:` reverse-DNS namespace string and
hash it with `sha256sum` — for example, `com.ardju.utils:foo:<nonce>`
for a hypothetical `foo` tool. The resulting hash domains are
disjoint: two tools deriving from the same nonce produce unrelated
256-bit outputs, so compromise of one tool's `STATIC_PW` reveals
nothing about another.

A tool that re-uses the literal `com.ardju.utils:shellx:` namespace
would produce the same `STATIC_PW` as shellx itself, allowing it to
decrypt shellx stores. Pick a distinct namespace.

### Side channels in ChaCha20 implementation

`shellx` ships its own ~80-line pure-Python ChaCha20. It is not
constant-time (Python makes true constant-time very hard), but it
operates on attacker-supplied ciphertext only — there is no realistic
side-channel adversary here.

### `~/.cache/shellx/` plaintext exposure window

During `shellx export` with `--no-encrypt`, a plaintext JSONC file
briefly exists at the destination you specified (e.g.,
`/tmp/audit/encrypted_*.jsonc`) for the duration of your manual review.
**Delete it as soon as you're done.**

The **default** mode (no `--no-encrypt`) does NOT write plaintext
anywhere — it pipes directly through `chezmoi encrypt`.

### `chezmoi` not available

`shellx export` requires `chezmoi` (for `chezmoi encrypt` and
`chezmoi source-path`) in the **default** (encrypt) mode. If chezmoi
is missing or misconfigured, the export fails with a clear error.

`shellx import` requires `chezmoi` (for `chezmoi decrypt`).

Runtime injection (`shellx --tag=… -- proc …`) requires **only Python 3**.

## When to upgrade to a real secret manager

`shellx` is appropriate for:

- Personal machines, single user, low-throughput secret use.
- API tokens, deploy keys, OAuth refresh tokens.
- A handful of secrets (< 100) that change infrequently.

It is **not** appropriate for:

- Team-shared secret rotation with audit logs.
- Compliance regimes (SOC2, HIPAA) requiring key access logging.
- High-frequency secret use (hundreds of invocations per minute).
- Multi-user systems with mutual distrust.

For those, use HashiCorp Vault, AWS Secrets Manager, or 1Password CLI.