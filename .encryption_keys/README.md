# Dotfiles encryption keys

This directory holds [age](https://github.com/FiloSottile/age) encryption keys used by chezmoi to encrypt/decrypt dotfiles secrets.

## How chezmoi uses this directory

[`.chezmoi.yaml.tmpl`](../.chezmoi.yaml.tmpl) scans this directory at template-render time:

| Glob pattern          | chezmoi field           | Purpose                                    |
| --------------------- | ----------------------- | ------------------------------------------ |
| `*.public.key`        | `age.recipientsFiles`   | Keys that can **encrypt** (recipients).    |
| `*.secret.key`        | `age.identities`        | Keys that can **decrypt** (identities).    |

The globs are relative to the chezmoi source directory, so every matching file in this folder is automatically included.

## Key naming conventions

- `<name>.public.key` — age recipient (public key). **Commit to git.**
- `<name>.secret.key` — age identity (private key). **Never commit.** The local `.gitignore` excludes `*.secret.key`.
- `<name>.secret.key.pgp` — private key wrapped with GPG. Safe to commit because only someone who holds the corresponding GPG private key can unwrap it.

The `<name>` is arbitrary; it typically identifies the machine, role, or user the key belongs to (e.g. `local`, `work-laptop`, `master`).

## Creating new keys

```bash
# Generate an age key pair (writes both private + public to stdout, but we split them below):
age-keygen -o local.secret.key
# The public key is embedded in the secret key file. Extract it:
age-keygen -y local.secret.key > local.public.key
```

## Wrapping a secret key with GPG

If you want to commit an encrypted copy of your secret key so you can bootstrap a new machine:

```bash
gpg --encrypt --recipient "your-gpg-key-id" local.secret.key
# This produces local.secret.key.pgp (if using default .gpg suffix, rename to .pgp).
```

The `.pgp` file is **not** picked up by chezmoi automatically — it is a backup. Decrypt it manually on a new machine before running chezmoi.

## Current keys

| File                        | Git tracked | Purpose                         |
| --------------------------- | ----------- | ------------------------------- |
| `local.public.key`          | yes         | Local machine recipient.        |
| `local.secret.key`          | no          | Local machine identity.         |
| `local.secret.key.pgp`      | yes         | GPG-wrapped local identity.     |
| `chezmoi-v2.public.key`     | yes         | Secondary recipient.            |
| `master.public.key`         | yes         | Master/fallback recipient.      |

## Adding a key from another machine

1. Copy the other machine's `*.public.key` into this directory.
2. Run `chezmoi update` — the yaml template will pick it up automatically.
3. Re-encrypt any affected secret files so the new recipient can decrypt them:
   ```bash
   chezmoi re-encrypt
   ```
