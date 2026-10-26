# AGENTS.md

## Purpose
Personal dotfiles managed with Chezmoi v2.70.4+, age encryption for secrets, Zsh with zgenom/p10k.

## Stack
- **Config**: chezmoi v2.70.4+, `.chezmoi.yaml.tmpl` (age encryption, auto key discovery)
- **Encryption**: age for files, gpg for age-key backups, Python stdlib scrypt + ChaCha20 + HMAC-BLAKE2b for shellx (no pip/venv)
- **Shell**: zsh, zgenom (plugin manager), powerlevel10k (prompt)
- **Agent tooling**: OpenCode (shared rules and skills under `dot_agents/`, deployed to `~/.agents/`)

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
- After a refactor that does not change the source directory layout, run `git status --short`, stage, and commit the working tree before ending the session. If the refactor changes the layout, ask first and do not commit.
- Put shared agent skills in `.agents/skills/<name>/SKILL.md` — the one location OpenCode, Codex, Copilot, Cursor, Gemini CLI, Zed, goose, Amp, and Factory Droid all scan natively. Do not copy them into a per-harness directory.
- **Add global rules and skills via `dot_agents/`, never via `chezmoi add ~/.agents/…`.** Both source trees target `~/.agents/`, and chezmoi resolves the collision by shadowing — `chezmoi add ~/.agents/rules/x.md` lands in the non-deploying `.agents/` tree, and the file never reaches `$HOME`. Edit `dot_agents/rules/` or `dot_agents/skills/` instead, then `chezmoi apply`.
- **Put a rule that names one harness's tool under `dot_config/<vendor>/rules/`.** A shared rule in `dot_agents/rules/` reaches every harness, so it must not depend on a tool that only one harness has. Load the per-harness file with that harness's own `instructions` glob in `dot_config/<vendor>/private_*.jsonc`.

### ⚠️ Ask first
- Adding new encryption keys (triggers `chezmoi re-encrypt` across all files)
- Changes to `.chezmoiignore` or `.chezmoidata.yaml`
- Structural changes to the source directory layout

### 🚫 Never
- Read or include content from encrypted files. The patterns are listed in `.agents/rules/chezmoi-source-project.md`
- Commit plaintext secrets, keys, tokens, or credentials
- Encrypt a file without running `chezmoi re-encrypt` afterwards
- Never modify `.encryption_keys/`. Adding a recipient key rewrites every encrypted file, so run `chezmoi re-encrypt` only after the user approves.
- Put a harness's own config in `.agents/<vendor>/` expecting another harness to read it — only `.agents/skills/` is a shared discovery location

## Pointers
- **`README.md`** — human-facing project overview, features, installation, usage, contributing
- **Subagent fleet case study** (haru/natsu/aki/fuyu/shiki): `docs/agent-case-studies.md` (the fleet itself was retired with Kilo on 2026-10-24; the reusable lessons live here)
- **Full chezmoi conventions + prefix tables**: `.agents/skills/chezmoi/SKILL.md`
- **Project rules**: `.agents/rules/chezmoi-source-project.md` (loaded by every harness through its own `instructions` glob)
- **Agent-context conventions (AGENTS.md, SKILL.md)**: `.agents/skills/agent-context/SKILL.md`
- **Knowledge cache convention + required `README.md` index**: `.agents/docs/cache/README.md` (full spec: `dot_agents/skills/project-context/references/knowledge-cache.md`)
- **Canonical on-disk project layout** (`.agents/`, `.tmp/` subroles, knowledge cache, vendor unification): `dot_agents/skills/project-layout/SKILL.md` (deployed to `~/.agents/skills/project-layout/`)
- **Document conventions** (filename, frontmatter, section order): `dot_agents/skills/document-conventions/SKILL.md` (deployed to `~/.agents/skills/document-conventions/`)
- **Local chezmoi/sprig documentation**: `.help/README.md`, `.help/DOCS_MAP.md`, `.help/QUIRKS.md`
- **Personal rules** (sudo-ask, ssh-read-allowlist, …): `dot_agents/rules.personal.d/` (deployed to `~/.agents/rules.personal.d/`)
- **SSH keys, gpg-agent, and live output over ssh**: `dot_agents/skills/ssh/SKILL.md` (deployed to `~/.agents/skills/ssh/`)
- **Harness-specific rules (OpenCode only)**: `dot_config/opencode/rules/` (deployed to `~/.config/opencode/rules/`, loaded by the `instructions` glob in `dot_config/opencode/private_opencode.jsonc`)
