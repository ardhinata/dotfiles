# chezmoi-dotfiles

- **Purpose**: Personal dotfiles managed with Chezmoi v2.70.4+, age encryption for secrets, Zsh with zgenom/p10k
- **Stack**: chezmoi, age (encryption), gpg (SSH agent), openssl, zsh, zgenom, powerlevel10k
- **Commands**: `chezmoi apply`, `chezmoi diff`, `chezmoi edit ~/.<file>`, `chezmoi add ~/.<file>`, `chezmoi update`, `chezmoi re-encrypt`
- **Project structure**: `dot_*/` → target `~/.config/`, `~/.shell/`, `~/.ssh/`; `.encryption_keys/` — age keypairs; `.encrypted_data/tokens/` — profile-scoped token snippets; `.help/` — AI agent reference docs
- **Boundaries**: Never read encrypted file contents (`.age`, `.asc`, `.decrypted`). Never commit plaintext secrets. Encrypted files are always gitignored.
- **Pointers**: `.kilo/skills/chezmoi/SKILL.md` (full conventions, prefix tables, template guidelines), `.help/QUIRKS.md` (edge cases), `.help/DOCS_MAP.md` (doc index), `README.md` (project overview)
