# dotfiles

[![Chezmoi](https://img.shields.io/badge/chezmoi-2.70.4+-blue?logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMjQgM0wzIDExVjI1QzMgMzUgMTIuNSA0My4yIDI0IDQ1QzM1LjUgNDMuMiA0NSAzNSA0NSAyNVYxMUwyNCAzWiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=)](https://chezmoi.io)

Personal dotfiles managed with [Chezmoi](https://chezmoi.io), using [age](https://github.com/FiloSottile/age) encryption for secrets. Shell configuration uses [Zsh](https://www.zsh.org/) with [zgenom](https://github.com/jandamm/zgenom) plugin manager and [Powerlevel10k](https://github.com/romkatv/powerlevel10k) prompt theme.

## Features

- **Encryption-first secrets** — SSH keys, API tokens, and sensitive config files are age-encrypted at rest in the source directory. Only machines with the corresponding private keys can decrypt them.
- **Profile-based machine differentiation** — A machine profile (`personal-laptop`, `home`, `office`, etc.) drives which encrypted secrets and configurations are deployed to each machine.
- **Dynamic key discovery** — Age encryption keys in `.encryption_keys/` are auto-discovered via glob patterns — no config changes needed when adding or removing keys.
- **Smart file exclusion** — Encrypted files that cannot be decrypted with available keys are automatically ignored at apply time, preventing errors on machines without a full key set.
- **Secure environment injection** — Environment variables for API tokens and secrets are encrypted at rest and injected on-demand at process launch via `runpriv`, avoiding persistent token exposure in the shell environment.
- **Plugin-driven Zsh** — Modular shell configuration via zgenom with Prezto modules: completion, syntax highlighting, history search, git, prompt, and more.
- **Hardened SSH configuration** — Global SSH hardening (strong host key/KEX/MAC algorithms, strict host key checking) with encrypted per-host config includes and visual host keys.
- **GPG-backed SSH agent** — SSH authentication via `gpg-agent` with automatic `SSH_AUTH_SOCK` setup.
- **Git configuration** — Global Git settings with conditional includes for work repositories.
- **Kilo AI agent config** — Managed configuration for the [Kilo](https://kilo.ai) AI coding assistant with model routing, MCP servers, and project rules.

## Prerequisites

- [Chezmoi](https://chezmoi.io/docs/install/) v2.70.4 or later
- [age](https://github.com/FiloSottile/age#installation) (file encryption tool)
- [Zsh](https://www.zsh.org/) (primary shell)
- `curl` or `wget` (for gitignore alias and documentation fetching)
- `gpg` (for SSH agent and key management)

## Installation

### On a new machine

```bash
# 1. Install chezmoi
sh -c "$(curl -fsLS get.chezmoi.io)"

# 2. Apply this dotfiles repo
chezmoi init --apply <repo-url>
```

### Bootstrap with age keys

Age private keys are backed up as GPG-encrypted files in `.encryption_keys/`. To restore them:

```bash
# Decrypt the age secret key from its GPG-wrapped backup
gpg --decrypt ~/.local/share/chezmoi/.encryption_keys/<key>.secret.key.asc \
  > ~/.local/share/chezmoi/.encryption_keys/<key>.secret.key
```

Then run `chezmoi apply` as normal.

### Local development

```bash
git clone <repo-url>
cd chezmoi-dotfiles
chezmoi init --apply
```

## Project Structure

```
.
├── .chezmoi.yaml.tmpl          # Chezmoi config template — age encryption, key auto-discovery
├── .chezmoidata.yaml           # Static template data (source paths, machine profile)
├── .chezmoiignore              # Templated exclusion rules (dynamic decryption checks)
├── .chezmoiversion             # Minimum Chezmoi version: 2.70.4
├── .gitignore
│
├── .chezmoiexternals/
│   └── zgenom.yaml             # External source: zgenom plugin manager (weekly refresh)
│
├── .encrypted_data/            # Age-encrypted secret snippets
│   └── tokens/                 # Profile-specific encrypted token exports (e.g., <profile>_<name>.zsh.age)
│
├── .encryption_keys/           # Age encryption keys
│   ├── README.md               # Key management documentation
│   ├── .gitignore              # Ignores unencrypted private keys
│   ├── *.public.key            # Public keys (committed) — used for encryption
│   ├── *.secret.key            # Private keys (gitignored) — used for decryption
│   ├── *.secret.key.age        # age-encrypted private key backup (committed)
│   └── *.secret.key.asc        # GPG-encrypted private key backup (committed)
│
├── .shell_helper/
│   └── check_decrypt.sh        # Script to test which encrypted files are decryptable
│
├── .help/                      # AI agent reference materials
│   ├── README.md
│   ├── DOCS_MAP.md             # Index of Chezmoi + Sprig documentation files
│   ├── QUIRKS.md               # Documented edge cases and mitigations for chezmoi templates
│   ├── fetch_current_docs.sh   # Downloads Chezmoi docs + Sprig docs
│   ├── chezmoi-docs/           # Local Chezmoi documentation (populated by fetch script)
│   └── sprig-docs/             # Local Sprig template function docs (populated by fetch script)
│
├── .kilo/                      # Kilo AI agent project config
│   ├── kilo.jsonc              # Agent model, MCP server, and routing configuration
│   ├── package.json            # Project dependencies (@kilocode/plugin)
│   └── rules/
│       └── chezmoi-source-project.md  # Project-specific agent rules
│
├── dot_config/                 → ~/.config/
│   └── kilo/
│       ├── kilo.jsonc.tmpl     # Kilo agent configuration (templated)
│       └── rules/
│           ├── ambiguity-resolution.md    # Agent instruction: when to ask for clarification
│           └── rtk-rules.md.tmpl          # RTK token-optimized CLI proxy rules
│
├── dot_gitconfig               → ~/.gitconfig
│   # Git identity, signing key, aliases, conditional work include
│
├── dot_p10k.zsh                → ~/.p10k.zsh
│   # Powerlevel10k prompt configuration (lean style)
│
├── dot_zprofile                → ~/.zprofile
│   # Sources ~/.profile
│
├── dot_shell/                  → ~/.shell/
│   ├── zsh/
│   │   └── 10-common-export.zsh     # EDITOR, SSH_AUTH_SOCK, runpriv alias
│   ├── helper/
│   │   ├── runpriv.tmpl              # On-demand environment variable injector
│   │   └── encrypt_store.sh.tmpl    # Secure environment variable encryption utility
│   └── private_store/               # Encrypted environment variable JSON stores
│       └── encrypted_private_<profile>_environment_store.json.age
│
├── dot_ssh/                    → ~/.ssh/
│   ├── config                  # SSH client config with hardened defaults
│   ├── config.d/               # Per-host/machine encrypted SSH configs
│   │   ├── .gitignore          # Ignores unencrypted *.conf files
│   │   └── encrypted_*.conf.age  # Age-encrypted per-host SSH configs
│   └── keys/                   # Encrypted SSH key pairs
│       ├── .gitignore
│       ├── encrypted_private_*.key.age       # Encrypted SSH private keys
│       └── encrypted_private_*.key.pub.age   # Encrypted SSH public keys
│
└── dot_zshrc                   → ~/.zshrc
    # Zsh configuration via zgenom + Prezto modules
```

## Usage

### Common commands

```bash
# Apply all changes to the target machine
chezmoi apply

# Preview changes without applying
chezmoi diff

# Edit a managed file in the source directory
chezmoi edit ~/.zshrc

# Add a new file to manage
chezmoi add ~/.someconfig

# Update from remote and apply
chezmoi update

# Re-encrypt all age-encrypted files (e.g., after adding a new recipient key)
chezmoi re-encrypt
```

### Machine profiles

This dotfiles repo supports per-machine profiles for managing environment-specific secrets:

1. Set the profile in `.chezmoidata.yaml`:
   ```yaml
   system_environment:
     profile: "home"   # or "office", "work-laptop", etc.
   ```

2. Create encrypted token files matching the profile name in `.encrypted_data/tokens/`:
   ```bash
   printf 'export TOKEN_NAME="secret-value"\n' \
     | age -e -a -R .encryption_keys/<recipient>.public.key \
       -o ".encrypted_data/tokens/<profile>_<name>.zsh.age"
   ```

3. Tokens are automatically decrypted and sourced at shell startup.

### Secure environment injection

The `runpriv` helper launches processes with secrets injected from an encrypted JSON store:

```bash
# Store an environment variable
encrypt_store.sh set GITHUB_TOKEN "<value>" --tags github,api

# Run a command with matching secrets injected
runpriv gh pr list  # injects all GITHUB_TOKEN-tagged secrets
```

Environment variables are encrypted with OpenSSL ChaCha20 and stored in `~/.shell/store/`. Only the secrets matching the command's tags are exposed — never persisted in the shell environment or shell history.

The injected process also receives `RUNPRIV_VARS`, a comma-separated list of the injected secret names (e.g., `GITHUB_TOKEN,NPM_TOKEN`), so scripts can introspect which secrets are available.

### SSH configuration workflow

SSH config fragments are stored as age-encrypted files:

1. Write your plaintext SSH config fragment
2. Encrypt it:
   ```bash
   age -e -a -R .encryption_keys/<recipient>.public.key \
     -o dot_ssh/config.d/encrypted_<descriptor>.conf.age \
     <plaintext-file>
   ```
3. The main `~/.ssh/config` includes all `config.d/*.conf` files automatically
4. Encrypted SSH keys in `dot_ssh/keys/` are decrypted by chezmoi during apply

### Adding a new encryption key

1. Generate a key pair:
   ```bash
   age-keygen -o <name>.secret.key
   age-keygen -y <name>.secret.key > <name>.public.key
   ```
2. Place `<name>.public.key` in `.encryption_keys/` and commit it
3. Place `<name>.secret.key` in `.encryption_keys/` (gitignored)
4. Optionally, create a GPG-wrapped backup:
   ```bash
   gpg -e -a -o .encryption_keys/<name>.secret.key.asc <name>.secret.key
   ```
5. Run `chezmoi re-encrypt` to update all encrypted files to include the new recipient
6. Commit the re-encrypted files

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

The `.chezmoiignore` template runs `check_decrypt.sh` at evaluation time, which:

1. Checks which `*.secret.key` files exist in `.encryption_keys/`
2. Attempts to decrypt each `encrypted_*` file with available keys
3. Outputs target paths for files that **cannot** be decrypted
4. Those files are silently skipped during `chezmoi apply`

This allows sharing a single repository across multiple machines without each machine needing every key.

## Contributing

Contributions are welcome. Here's how to get involved:

1. **Fork the repository** and create a feature branch
2. **Follow the existing conventions**:
   - Encrypt any new sensitive files with age before committing
   - Use Chezmoi naming conventions (`dot_` prefix for `.` files, `encrypted_` prefix for encrypted files)
   - Encrypted files should be accompanied by corresponding public keys in `.encryption_keys/`
3. **Test your changes**: Run `chezmoi diff` to verify the expected output before applying
4. **Submit a pull request** with a clear description of the changes

## License

This project is unlicensed — it is released into the public domain for personal use. No rights reserved.

If you use this as a reference or starting point for your own dotfiles, attribution is appreciated but not required.
