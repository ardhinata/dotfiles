# dotfiles

[![Chezmoi](https://img.shields.io/badge/chezmoi-2.70.4+-blue)](https://chezmoi.io)

Personal dotfiles managed with [Chezmoi](https://chezmoi.io). Secrets are stored with [age](https://github.com/FiloSottile/age) encryption. The shell is [Zsh](https://www.zsh.org/). It uses the [zgenom](https://github.com/jandamm/zgenom) plugin manager and the [Powerlevel10k](https://github.com/romkatv/powerlevel10k) prompt.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Secrets stay encrypted.** SSH keys, API tokens, and sensitive config files are stored as age-encrypted blobs in the source directory. Only a host that holds the matching private key can decrypt them.
- **Per-machine profiles.** A machine profile (`personal-laptop`, `home`, `office`, …) decides which encrypted secrets and configurations deploy to each host.
- **Key discovery is automatic.** Age keys under `.encryption_keys/` are found through glob patterns. No config change is needed when a key is added or removed.
- **Files skip cleanly when keys are missing.** Encrypted files that the current host cannot decrypt are removed from the apply set. A host without every key still applies what it can.
- **Secrets enter processes only when needed.** Environment variables for tokens and API keys are encrypted at rest. `shellx` injects them at process launch, so they are not exposed through the shell. `shellx` runs on Python 3 stdlib, with no `pip` and no venv. It uses an opaque on-disk format, JSONC export and import to the chezmoi source tree, and zsh completion. See `dot_shell/helper/.help/` (source-only) for the full design.
- **Zsh is plugin-driven.** Modular shell configuration through zgenom and Prezto modules: completion, syntax highlighting, history search, git, prompt, and more.
- **SSH is hardened.** Global SSH hardening (strong host-key, KEX, and MAC algorithms, strict host-key checking) with age-encrypted per-host config includes and visual host keys.
- **The SSH agent is GPG.** SSH authentication runs through `gpg-agent`. `SSH_AUTH_SOCK` is set automatically.
- **Git config is portable.** Global Git settings carry conditional includes for work repositories.
- **Agent tooling is managed.** OpenCode, Magic Context, and AFT configs, the cc-safety-net destructive-command policy, and the global agent rules and skills all deploy from this tree. The project-scope `.agents/` tree stays in the repo and never reaches `$HOME`.

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
├── .chezmoi.yaml.tmpl      # Chezmoi config template (age, key discovery)
├── .chezmoidata.yaml       # Static template data (paths, profile)
├── .chezmoiignore          # Templated exclusion rules (decryption checks)
├── .chezmoiversion         # Minimum Chezmoi version: 2.70.4
├── .chezmoiscripts/        # Post-apply hooks
├── .chezmoiexternals/      # Externally managed trees (zgenom, TPM, themes)
├── AGENTS.md               # Instructions for coding agents
│
├── .agents/                # Project-scope agent tree (never deployed)
│   ├── docs/cache/         # Curated knowledge cache
│   ├── opencode/           # Project-scope OpenCode config
│   ├── rules/              # Project-scope rule files
│   └── skills/             # Project-scope skills
├── dot_agents/             # Global agent tree → ~/.agents/
│   ├── exact_rules/        # Shared rules → ~/.agents/rules/
│   ├── exact_rules.opencode/  # OpenCode-only rules
│   ├── rules.personal.d/   # Personal rules
│   └── skills/             # Global skills → ~/.agents/skills/
│
├── .encrypted_data/        # Source-only secret data
│   └── env_store/          # shellx exports (age-encrypted JSONC)
├── .encryption_keys/       # Age encryption keys
├── .shell_helper/          # Template helpers (never deployed)
│   └── check_decrypt.sh    # Tests which encrypted files are decryptable
├── .help/                  # Local chezmoi and sprig documentation
│
├── dot_config/             → ~/.config/
│   ├── alacritty/          # Terminal emulator config
│   ├── tmux/               # Terminal multiplexer config
│   ├── zed/                # Editor config
│   ├── opencode/           # OpenCode config and rules
│   ├── private_cortexkit/  # Magic Context and AFT config
│   └── systemd/user/       # Embeddings proxy unit
├── dot_gitconfig           → ~/.gitconfig
├── dot_local/share/private_shellx/  # Master key template (0600)
├── dot_p10k.zsh            → ~/.p10k.zsh
├── dot_shell/              → ~/.shell/
│   ├── helper/             # shellx, pinentry wrappers, embeddings proxy
│   ├── private_store/      # Legacy ejson store (still deployed)
│   └── zsh/                # Zsh modules and completions
├── dot_ssh/                → ~/.ssh/
├── dot_zprofile            → ~/.zprofile
├── dot_zshrc               → ~/.zshrc
├── private_dot_cc-safety-net/  # → ~/.cc-safety-net/ (destructive-command policy)
├── private_dot_gnupg/      # → ~/.gnupg/ (gpg and gpg-agent config)
└── docs/                   # Human-facing docs (plans, reports, post-mortems)
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

`.chezmoidata.yaml` holds a free-form profile name for the machine. The
`shellx` export header records it. The profile does not select secrets.
Every secret lives in the shellx store under the same variable name on
every machine.

### Shell-wide secret variables

The `shellx` store is process-scoped: it injects a secret only into the
process that asks for it. Some secrets must be present in every shell
instead. The `shellx env` subcommand prints one `export` line per variable,
and `dot_shell/zsh/20-secret-env-load.zsh` sources it at shell startup.

`dot_zshrc` sources that file. The helper decrypts on every shell start.
One variable costs about 42 ms, so keep the list short.

The value never rests on disk in plaintext. The previous ejson store
decrypted at `chezmoi apply` time and left the value in a mode-0600 file
under `~/.shell/zsh/`. Restore the store on a new machine with
`shellx import`, as described below.

### Secure environment injection

`shellx` launches processes with secrets injected from an opaque on-disk
store. It replaces the older `runpriv` and `encrypt_store.sh` helpers. It
uses Python 3 stdlib only, with no `pip` and no venv, and it avoids common
credential-file signatures.

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

Secrets are encrypted with ChaCha20 under keys derived from the master key.
A new blob derives its keys with HMAC-SHA512 over a per-blob salt. The tag
is HMAC-BLAKE2b over the associated data and the ciphertext. The associated
data binds the blob to its own header and to the variable name, so a
swapped blob fails to authenticate. Blobs written by an older version
derive their keys with scrypt, and both versions live in one store.

The output is an opaque binary blob kept under `~/.local/share/<32-hex-slug>/`.
The slug and the per-secret filenames are blake2b hashes, so they look like
app-cache noise to a static scanner. See `dot_shell/helper/.help/`
(source-only) for the full design, the crypto, and the limitations.

The injected process also receives `SHELLX_VARS`, and the legacy
`RUNPRIV_VARS` alias with the same value. Both hold a comma-separated list
of injected secret names. Scripts use it to introspect which secrets are
present.

#### Export to and import from the chezmoi source tree

```bash
shellx export   # Writes an age-encrypted JSONC export to the chezmoi source tree

# Restore on another host.
shellx import ~/.local/share/chezmoi/.encrypted_data/env_store/encrypted_*.jsonc.age
```

Exports are JSONC (JSON with `//` comments) with per-entry metadata in the
comments, so they stay readable, editable, and diffable. The plaintext JSONC
is piped through `chezmoi encrypt` and never touches disk. `.chezmoiignore`
excludes the resulting blobs from `chezmoi apply`, so restoration is
explicit through `shellx import`.

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

One repository serves many hosts. Each host applies only the secrets it can
decrypt.

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
chezmoi apply  ─── age -d -i <secret-key>
      │
      ▼
Plaintext restored at target path (~/.ssh/..., ~/.shell/..., etc.)
```

### Dynamic ignore mechanism

The `.chezmoiignore` template runs `check_decrypt.sh` at evaluation time.
The script checks which age identities the host holds. It then tries to
decrypt every `encrypted_*` file, and prints the target paths of the files
it cannot decrypt. Those files are then skipped during `chezmoi apply`.

The script prunes dot-directories, because chezmoi ignores every
dot-directory at the source root except `.chezmoi*`. Without the prune the
walk descends into `.tmp`, which holds over a hundred thousand files, on
every chezmoi command. See `.shell_helper/README.md` for the full script
documentation.

## Contributing

Contributions are welcome.

1. **Fork the repository** and create a feature branch.
2. **Follow the existing conventions**:
   - Encrypt every new sensitive file with age before committing.
   - Use Chezmoi naming conventions: `dot_` prefix for `.` files, `encrypted_` prefix for encrypted files.
   - Pair each encrypted file with a public key in `.encryption_keys/`.
3. **Test your changes**: run `chezmoi diff` to verify the expected output before applying.
4. **Submit a pull request** with a clear description of the changes.

Coding agents should read [`AGENTS.md`](AGENTS.md) first.

## License

This project is released into the public domain. No rights reserved.

If you use this repository as a starting point for your own dotfiles, attribution is appreciated but not required.

Kept as-is: "Age" / "GPG" / "ChaCha20" / "HMAC-BLAKE2b" / "HMAC-SHA512" / "scrypt" — cryptographic primitives with fixed names, kept as written.
Kept as-is: `<repo-url>`, `<key>`, `<name>`, `<recipient>`, `<profile>`, `<descriptor>` — placeholder tokens left literal so the user knows what to substitute.
