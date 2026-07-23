# AGENTS.md

## Purpose
Personal dotfiles managed with Chezmoi v2.70.4+, age encryption for secrets, Zsh with zgenom/p10k.

## Stack
- **Config**: chezmoi v2.70.4+, `.chezmoi.yaml.tmpl` (age encryption, auto key discovery)
- **Encryption**: age for files, gpg for age-key backups, Python stdlib scrypt + ChaCha20 + HMAC-BLAKE2b for shellx (no pip/venv)
- **Shell**: zsh, zgenom (plugin manager), powerlevel10k (prompt)

## Commands
- `chezmoi apply` — apply changes; add `--dry-run` to preview
- `chezmoi diff` — show unapplied changes
- `chezmoi edit ~/.<file>` — edit managed file in source dir
- `chezmoi add ~/.<file>` — add new file to management
- `chezmoi update` — pull + apply
- `chezmoi re-encrypt` — re-encrypt all age files after adding a recipient key
- `bash .help/fetch_current_docs.sh` — refresh local chezmoi + sprig API docs

## Code style
- For chezmoi templates: **load the `chezmoi` skill** — it covers prefix tables (`dot_`, `encrypted_`), source-state attributes, and template function guidelines. Validate assumptions against `.help/chezmoi-docs/` and `.help/QUIRKS.md`.
- For agent-context files (`AGENTS.md`, `SKILL.md`): **load the `agent-context` skill** — it covers the agents.md open standard and the agentskills.io spec + best practices.

## Testing rules
- Always run `chezmoi diff` before applying to verify expected output.
- After `chezmoi re-encrypt`, run `chezmoi apply --dry-run` first to catch decryption failures.

## Boundaries

### ✅ Always
- Load the `chezmoi` skill before editing any template file
- Validate chezmoi behavior against `.help/chezmoi-docs/` or `.help/QUIRKS.md`
- Run `bash .help/fetch_current_docs.sh` if `.help/chezmoi-docs/` is missing
- After a structural refactor that adds, renames, or deletes files, run `git status --short`, stage, and commit the working tree before ending the session

### ⚠️ Ask first
- Adding new encryption keys (triggers `chezmoi re-encrypt` across all files)
- Changes to `.chezmoiignore` or `.chezmoidata.yaml`
- Structural changes to the source directory layout

### 🚫 Never
- Read or include content from encrypted files (`.age`, `.asc`, `.decrypted`)
- Commit plaintext secrets, keys, tokens, or credentials
- Encrypt a file without running `chezmoi re-encrypt` afterwards
- Modify `.encryption_keys/` without understanding the re-encrypt workflow

## Pointers
- Project overview: `README.md`
- Full chezmoi conventions + prefix tables: `.kilo/skills/chezmoi/SKILL.md`
- Project rules: `.kilo/rules/chezmoi-source-project.md`
- Agent-context conventions (AGENTS.md, SKILL.md): `.kilo/skills/agent-context/SKILL.md`
- Knowledge cache convention and required `README.md` index: `dot_config/kilo/skills/project-context/references/knowledge-cache.md`
- Local documentation index: `.help/README.md`
- Edge cases (decrypt abort, etc.): `.help/QUIRKS.md`
- Doc index (chezmoi + sprig): `.help/DOCS_MAP.md`
