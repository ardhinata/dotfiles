# Crypto

`shellx` uses **only** the Python 3 standard library for all cryptography.
No `pip install`, no virtualenv, no third-party wheels.

## Cipher suite

| Primitive | Algorithm | Source |
|---|---|---|
| Password-based KDF | **scrypt** (`N=2¹⁵, r=8, p=1, dklen=64`) | `hashlib.scrypt` |
| Stream cipher | **ChaCha20** (RFC 7539) | ~80-line reference impl inline |
| Authentication | **HMAC-BLAKE2b-256** truncated to 128 bits | `hmac` + `hashlib.blake2b` |
| Key length | 32 bytes (encryption) + 32 bytes (MAC) | derived via scrypt |

The 64-byte scrypt output is split into:

```
derived[0:32]   → enc_key   (ChaCha20 key)
derived[32:64]  → mac_key   (HMAC-BLAKE2b key)
```

## Password (STATIC_PW)

Same value the legacy helpers used; rendered at chezmoi apply time:

```text
STATIC_PW = sha256("chezmoi:" + sha512(profile))
```

`profile` is `system_environment.profile` from `.chezmoidata.yaml`. Two
machines with different profiles produce different static passwords, so a
store encrypted under one profile is unreadable on another — even if
the blob files are copied.

**Implication:** `shellx export` on profile `home` produces a blob that
`shellx import` cannot restore on profile `work-laptop` unless the
profile value is identical. This is by design — keep a per-profile
export, or change the profile before importing.

## Blob format (per-secret file)

```
+--------+--------+----------+----------+------+---------+
| MAGIC  | VER    | SALT     | NONCE    | TAG  | CT      |
| 4 B    | 1 B    | 16 B     | 12 B     | 16 B | N B     |
+--------+--------+----------+----------+------+---------+
  SHX1     0x01
```

- **MAGIC** — `b"SHX1"`. Identifies the file type without matching any
  well-known credential format.
- **VER** — protocol version (`0x01`). Bump on incompatible changes.
- **SALT** — random per blob (not per file group). 16 bytes.
- **NONCE** — random per blob, never reused (single-use per key, fine).
- **TAG** — `HMAC-BLAKE2b(key=mac_key, msg=AAD || CT)[:16]`.
- **CT** — ChaCha20(key=enc_key, nonce=NONCE, counter=0, plaintext).

## AAD construction

The AAD (associated data) binds the blob to its own header and to the
variable name. This prevents **blob-swap attacks** where an attacker
who can rewrite `.idx` swaps the encrypted payload of `GH_TOKEN` with
that of `NPM_TOKEN` — authentication fails.

```python
AAD = b"SHX1-AEAD1" + b"|" + SALT + b"|" + NONCE + b"|" + VAR_NAME.encode()
```

`MAGIC` and `VERSION` are fixed, so they are not re-included in the AAD;
the prefix `SHX1-AEAD1` plus the random SALT/NONCE provide domain
separation.

## Why scrypt instead of Argon2id?

Argon2id is the modern recommendation but has no stdlib implementation
in Python (would require `argon2-cffi`). scrypt via `hashlib.scrypt` is:

- ✅ Available on every distro Python 3.8+ (this project's floor).
- ✅ Memory-hard (`N=2¹⁵ × r=8 × 128 B ≈ 32 MiB` per derivation), which
  defeats GPU/ASIC brute force on the STATIC_PW.
- ✅ Adequate for the static-password threat model (STATIC_PW is
  64 hex = 256 effective bits, plus the per-blob salt = brute force is
  not the relevant attack).

If Argon2id support is needed, install `argon2-cffi` and patch
`_derive_keys` — the wire format stays compatible.

## Why ChaCha20 + HMAC instead of AES-GCM?

`hashlib` does not expose AES-GCM in the Python stdlib (only available
via `cryptography` package). An AEAD via ChaCha20 + HMAC-BLAKE2b
("Encrypt-then-MAC", RFC 7539 §2.8 spirit) is a well-known construction
with equivalent security properties for this use case.

The only subtle rule is **never reuse a (key, nonce) pair**. With
random 12-byte nonces per blob, collision probability is negligible
(2⁻⁹⁶ over the lifetime of the universe for < 2³² blobs).

## Constant-time verification

Authentication uses `hmac.compare_digest`, which avoids timing oracles.

## Memory hygiene

`shellx` zeroes plaintext buffers (`bytearray` reassignment to `b"\x00"*n`)
immediately after handing them to `os.environ` / `os.execvpe`. This is
**best-effort only**: CPython's GC may have already copied the bytes
elsewhere (string interning, etc.). True memory locking
(`mlock(2)`) is not exposed in stdlib and is intentionally out of scope.

## Threat-model fit

| Attack | Defended? |
|---|---|
| Grep for `token\|secret\|key\|password` in home dir | ✅ Path is random, content is opaque ciphertext, no JSON keys to match. |
| Read `~/.aws/credentials`, `~/.netrc`, etc. | ✅ Nothing is stored there. |
| Read `/proc/<pid>/environ` of running `shellx` | ⚠️ The *child process* sees the secrets only for its lifetime; `shellx` itself never exports them to its own env. |
| Read `/proc/<pid>/environ` of the launched child | ⚠️ Inherent to Unix; not preventable without breaking tool compatibility. See `LIMITATIONS.md`. |
| Brute-force the on-disk ciphertext offline | ✅ scrypt 2¹⁵/8/1 = ~32 MiB-memory, ~100 ms per attempt on modern CPU. |
| Modify `.idx` to point at wrong blob | ✅ AAD binds variable name to the ciphertext; mismatch fails auth. |
| Roll back to a previous (older) blob | ❌ No monotonic counter. Acceptable: rollback = same secrets, just older. |
| Memory dump of running process | ❌ Out of scope (see `LIMITATIONS.md`). |