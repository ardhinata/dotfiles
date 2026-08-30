# dotfiles

[![Chezmoi](https://img.shields.io/badge/chezmoi-2.70.4+-blue)](https://chezmoi.io)

Personal dotfiles managed with [Chezmoi](https://chezmoi.io). Secrets are stored with [age](https://github.com/FiloSottile/age) encryption. The shell is [Zsh](https://www.zsh.org/). It uses the [zgenom](https://github.com/jandamm/zgenom) plugin manager and the [Powerlevel10k](https://github.com/romkatv/powerlevel10k) prompt.

## Features

- **Secrets stay encrypted.** SSH keys, API tokens, and sensitive config files are stored as age-encrypted blobs in the source directory. Only a host that holds the matching private key can decrypt them.
- **Per-machine profiles.** A machine profile (`personal-laptop`, `home`, `office`, …) decides which encrypted secrets and configurations deploy to each host.
- **Key discovery is automatic.** Age keys under `.encryption_keys/` are found through glob patterns. No config change is needed when a key is added or removed.
- **Files skip cleanly when keys are missing.** Encrypted files that the current host cannot decrypt are removed from the apply set. A host without every key still applies what it can.
- **Secrets enter processes only when needed.** Environment variables for tokens and API keys are encrypted at rest. `shellx` injects them at process launch, so they are not exposed through the shell. `shellx` runs on Python 3 stdlib — no `pip`, no venv. It uses an opaque on-disk format, JSONC export and import to the chezmoi source tree, and zsh completion. See `dot_shell/helper/.help/` (source-only) for the full design.
- **Zsh is plugin-driven.** Modular shell configuration through zgenom and Prezto modules: completion, syntax highlighting, history search, git, prompt, and more.
- **SSH is hardened.** Global SSH hardening (strong host-key, KEX, and MAC algorithms, strict host-key checking) with age-encrypted per-host config includes and visual host keys.
- **The SSH agent is GPG.** SSH authentication runs through `gpg-agent`. `SSH_AUTH_SOCK` is set automatically.
- **Git config is portable.** Global Git settings carry conditional includes for work repositories.
- **Kilo is managed.** Configuration for the [Kilo](https://kilo.ai) AI coding assistant covers model routing, MCP servers, and project rules.

## Prerequisites

- [Chezmoi](https://chezmoi.io/docs/install/) v2.70.4 or later
- [age](https://github.com/FiloSottile/age#installation)
- [Zsh](https://www.zsh.org/)
- `curl` or `wget`
- `gpg` (for the SSH agent and key management)

## Installation

### New host

```bash
# 1. Install chezmoi.
sh -c "$(curl -fsLS get.chezmoi.io)"

# 2. Apply this dotfiles repo.
chezmoi init --apply <repo-url>
```

### Restore age keys

Age private keys are backed up as GPG-encrypted files in `.encryption_keys/`. To restore one:

```bash
gpg --decrypt ~/.local/share/chezmoi/.encryption_keys/<key>.secret.key.asc \
  > ~/.local/share/chezmoi/.encryption_keys/<key>.secret.key
```

Then run `chezmoi apply`.

### Local development

```bash
git clone <repo-url>
cd chezmoi-dotfiles
chezmoi init --apply
```

## Project Structure

```
.
├── .chezmoi.yaml.tmpl          # Chezmoi config template (age, key discovery)
├── .chezmoidata.yaml           # Static template data (paths, profile)
├── .chezmoiignore              # Templated exclusion rules (decryption checks)
├── .chezmoiversion             # Minimum Chezmoi version: 2.70.4
├── .gitignore
│
├── .chezmoiexternals/
│   └── zgenom.yaml             # External source: zgenom (weekly refresh)
│
├── .encrypted_data/            # Age-encrypted secret snippets
│   └── env_store/              # Profile-scoped encrypted env-var exports
│
├── .encryption_keys/           # Age encryption keys
│   ├── README.md               # Key management documentation
│   ├── .gitignore              # Ignores unencrypted private keys
│   ├── *.public.key            # Public keys (committed)
│   ├── *.secret.key            # Private keys (gitignored)
│   ├── *.secret.key.age        # age-encrypted private key backup (committed)
│   └── *.secret.key.asc        # GPG-encrypted private key backup (committed)
│
├── .shell_helper/
│   ├── check_decrypt.sh        # Tests which encrypted files are decryptable
│   └── README.md               # Helper script documentation
│
├── .help/                      # Agent reference materials
│   ├── README.md
│   ├── DOCS_MAP.md             # Index of Chezmoi and Sprig docs
│   ├── QUIRKS.md               # Documented edge cases for chezmoi templates
│   ├── fetch_current_docs.sh   # Downloads Chezmoi and Sprig docs
│   ├── chezmoi-docs/           # Populated by fetch_current_docs.sh
│   └── sprig-docs/             # Populated by fetch_current_docs.sh
│
├── .kilo/                      # Kilo AI agent project config
│   ├── kilo.jsonc              # Agent model, MCP servers, routing
│   ├── package.json            # Project dependencies (@kilocode/plugin)
│   ├── agent-manager.json      # Worktree state and session metadata
│   ├── rules/
│   │   └── chezmoi-source-project.md  # Project-specific agent rules
│   └── skills/
│       └── chezmoi/            # Chezmoi skill (source-state conventions)
│
├── dot_config/                 → ~/.config/
│   └── kilo/
│       ├── kilo.jsonc.tmpl     # Kilo agent configuration
│       ├── rules/              # Agent rules
│       └── skills/             # Agent skills
│
├── dot_gitconfig               → ~/.gitconfig
│
├── dot_p10k.zsh                → ~/.p10k.zsh
│
├── dot_zprofile                → ~/.zprofile
│
├── dot_shell/                  → ~/.shell/
│   ├── zsh/
│   │   ├── 00-before-zgenom.zsh        # Pre-plugin initialization
│   │   ├── 10-common-export.zsh         # EDITOR, SSH_AUTH_SOCK, shellx on PATH
│   │   ├── 15-zgenom-helper-func.zsh    # Helpers for zgenom-loaded plugins
│   │   └── completions/
│   │       └── _shellx.tmpl            # Zsh completion for shellx
│   ├── helper/
│   │   ├── executable_shellx                    # Secret manager (Python 3 stdlib)
│   │   ├── executable_shellx_completion_helper.tmpl
│   │   ├── .help/                               # shellx docs (source-only)
│   │   ├── executable_runpriv.tmpl              # LEGACY: superseded by shellx
│   │   └── executable_encrypt_store.sh.tmpl    # LEGACY: superseded by shellx
│   └── private_store/               # Encrypted JSON stores
│
├── dot_ssh/                    → ~/.ssh/
│   ├── config                  # Hardened SSH client config
│   ├── config.d/               # Per-host encrypted SSH configs
│   │   ├── .gitignore
│   │   └── encrypted_*.conf.age  # Age-encrypted per-host SSH configs
│   └── keys/                   # Encrypted SSH key pairs
│       ├── .gitignore
│       ├── encrypted_private_*.key.age       # Encrypted SSH private keys
│       └── encrypted_private_*.key.pub.age   # Encrypted SSH public keys
│
└── dot_zshrc                   → ~/.zshrc
```

## Usage

### Common commands

```bash
chezmoi apply         # Apply all changes to the target host
chezmoi diff          # Preview changes without applying
chezmoi edit ~/.zshrc # Edit a managed file in the source directory
chezmoi add ~/.<file> # Add a new file to management
chezmoi update        # Pull from remote and apply
chezmoi re-encrypt    # Re-encrypt all age files (after adding a recipient)
```

### Machine profiles

Per-host profiles control which environment-specific secrets deploy where.

1. Set the profile in `.chezmoidata.yaml`:
   ```yaml
   system_environment:
     profile: "home"   # or "office", "work-laptop", …
   ```

2. Create encrypted token files that match the profile name under `.encrypted_data/env_store/`:
   ```bash
   printf 'export TOKEN_NAME="secret-value"\n' \
     | age -e -a -R .encryption_keys/<recipient>.public.key \
       -o ".encrypted_data/env_store/<profile>_<name>.zsh.age"
   ```

3. Tokens are decrypted and sourced at shell startup.

### Secure environment injection

`shellx` launches processes with secrets injected from an opaque on-disk store. It replaces the older `runpriv` and `encrypt_store.sh` helpers. It uses Python 3 stdlib only — no `pip`, no venv — and avoids common credential-file signatures.

```bash
# First-time setup. Auto-runs on the first invocation; an explicit init also works.
shellx init

# Store an environment variable. The value is read from stdin or prompted.
printf '%s' 'ghp_xxxxxxxxxxxxxxxxxxxx' \
  | shellx store GH_TOKEN --tag=git,api --process=gh,glab

# Run a command with matching secrets injected.
shellx --tag=git gh pr list
# Equivalent form. Use it when you want zsh tab-completion for the target process.
shellx run --tag=git gh pr list
```

Secrets are encrypted with **scrypt + ChaCha20 + HMAC-BLAKE2b** under variable-name-bound AAD. The output is an opaque binary blob kept under `~/.local/share/<random-16-hex-slug>/`. The slug and per-secret filenames are blake2b hashes — indistinguishable from app-cache noise to a static scanner. See `dot_shell/helper/.help/` (source-only) for the full design, crypto, and limitations.

The injected process also receives `SHELLX_VARS` — and the legacy `RUNPRIV_VARS` alias with the same value — a comma-separated list of injected secret names. Scripts use it to introspect which secrets are present.

#### Export to and import from the chezmoi source tree

```bash
shellx export   # Writes an age-encrypted JSONC export to the chezmoi source tree

# Restore on another host.
shellx import ~/.local/share/chezmoi/.encrypted_data/env_store/encrypted_*.jsonc.age
```

Exports are JSONC (JSON with `//` comments) with per-entry metadata in the comments — readable, editable, diffable. The plaintext JSONC is piped through `chezmoi encrypt` and never touches disk. `.chezmoiignore` excludes the resulting blobs from `chezmoi apply`, so restoration is explicit through `shellx import`.

### SSH configuration workflow

Per-host SSH config fragments are stored as age-encrypted files.

1. Write the plaintext SSH config fragment.
2. Encrypt it:
   ```bash
   age -e -a -R .encryption_keys/<recipient>.public.key \
     -o dot_ssh/config.d/encrypted_<descriptor>.conf.age \
     <plaintext-file>
   ```
3. The main `~/.ssh/config` includes every `config.d/*.conf` file automatically.
4. Encrypted SSH keys in `dot_ssh/keys/` are decrypted by chezmoi during apply.

### Adding a new encryption key

1. Generate a key pair:
   ```bash
   age-keygen -o <name>.secret.key
   age-keygen -y <name>.secret.key > <name>.public.key
   ```
2. Place `<name>.public.key` in `.encryption_keys/` and commit it.
3. Place `<name>.secret.key` in `.encryption_keys/` (gitignored).
4. Optionally, create a GPG-wrapped backup:
   ```bash
   gpg -e -a -o .encryption_keys/<name>.secret.key.asc <name>.secret.key
   ```
5. Run `chezmoi re-encrypt` to update every encrypted file with the new recipient.
6. Commit the re-encrypted files.

## How It Works

### Encryption flow

```
Plaintext file
      │
      ▼
age -e -a -R <public-key> -o encrypted_file.age
      │
      ▼
Stored in source dir (committed)
      │
      ▼
chezmoi apply  ───  age -d -i <secret-key>
      │
      ▼
Plaintext restored at target path (~/.ssh/..., ~/.shell/..., etc.)
```

### Dynamic ignore mechanism

The `.chezmoiignore` template runs `check_decrypt.sh` at evaluation time. The script:

1. Checks which `*.secret.key` files exist in `.encryption_keys/`.
2. Tries to decrypt each `encrypted_*` file with the available keys.
3. Prints target paths for files that **cannot** be decrypted.
4. Those files are skipped during `chezmoi apply`.

One repository serves many hosts. Each host applies only the secrets it can decrypt.

## Contributing

Contributions are welcome.

1. **Fork the repository** and create a feature branch.
2. **Follow the existing conventions**:
   - Encrypt every new sensitive file with age before committing.
   - Use Chezmoi naming conventions: `dot_` prefix for `.` files, `encrypted_` prefix for encrypted files.
   - Pair each encrypted file with a public key in `.encryption_keys/`.
3. **Test your changes**: run `chezmoi diff` to verify the expected output before applying.
4. **Submit a pull request** with a clear description of the changes.

## License

This project is released into the public domain. No rights reserved.

If you use this repository as a starting point for your own dotfiles, attribution is appreciated but not required.

Kept as-is: "Age" / "GPG" / "scrypt + ChaCha20 + HMAC-BLAKE2b" — cryptographic primitives with fixed names, kept as written.
Kept as-is: `<repo-url>`, `<key>`, `<name>`, `<recipient>`, `<profile>`, `<descriptor>` — placeholder tokens left literal so the user knows what to substitute.
