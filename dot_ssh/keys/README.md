# SSH Keys

All files in this directory are age-encrypted (`encrypted_` prefix, `.age` suffix)
before being committed to version control.

## Why public keys are encrypted

SSH public keys contain a **comment field** (the last whitespace-delimited segment)
that typically includes an email address, username, or machine identifier. Examples:

```
ssh-ed25519 AAAAC3NzaC1l... comment-goes-here
ssh-rsa AAAAB3NzaC1yc2E... user@hostname
```

These comments may constitute **personally identifiable information** and in some
cases may be covered by **non-disclosure agreements** (e.g., client hostnames,
corporate email addresses, internal project names). To avoid accidental exposure,
public key files are encrypted alongside private keys.

## File naming

| Pattern | Content | Permissions |
|---|---|---|
| `encrypted_private_<name>.key.age` | Private key | 600 (owner-only, via `private_`) |
| `encrypted_private_<name>.key.pub.age` | Public key | 600 (owner-only, via `private_`) |

The `.gitignore` in this directory allows only `encrypted_*` files and itself.
Decrypted plaintext keys are never committed.
