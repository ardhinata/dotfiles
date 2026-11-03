# AGENTS.md

## Purpose
Personal dotfiles managed with Chezmoi v2.70.4+, age encryption for secrets, Zsh with zgenom/p10k. The repo also carries the global agent rules, skills and harness configs that deploy to `~/.agents/` and `~/.config/`.

## Stack
- **Config**: chezmoi v2.70.4+, `.chezmoi.yaml.tmpl` (age encryption, auto key discovery)
- **Encryption**: age for files, gpg for age-key backups
- **Secrets**: `shellx` in `dot_shell/helper/` (Python 3 stdlib, no pip/venv). It uses scrypt or HMAC-SHA512 key derivation, ChaCha20, and an HMAC-BLAKE2b tag. The master key renders to `~/.local/share/shellx/master.key` (0600).
- **Shell**: zsh, zgenom (plugin manager), powerlevel10k (prompt)
- **Embeddings**: local dimensions proxy in `dot_shell/helper/`, systemd unit in `dot_config/systemd/user/`
- **Agent tooling**: OpenCode, Magic Context and AFT configs in `dot_config/`. The cc-safety-net policy sits in `private_dot_cc-safety-net/`.
- **Global rules and skills**: `dot_agents/` (deployed to `~/.agents/`)

## Commands
- `chezmoi apply` — apply changes, and add `--dry-run` to preview
- `chezmoi diff` — show unapplied changes
- `chezmoi edit ~/.<file>` — edit managed file in source dir
- `chezmoi add ~/.<file>` — add new file to management
- `chezmoi update` — pull + apply
- `chezmoi re-encrypt` — re-encrypt all age files after adding a recipient key
- `bash .help/fetch_current_docs.sh` — refresh local chezmoi + sprig API docs

## Code style
- For chezmoi templates: **load the `chezmoi` skill** — it covers prefix tables (`dot_`, `encrypted_`), source-state attributes, and template function guidelines. Validate assumptions against `.help/chezmoi-docs/` and `.help/QUIRKS.md`.
- For `AGENTS.md`: **load the `project-context` skill** — it covers the agents.md open standard and the drafting workflow.
- For `SKILL.md`: **load the `document-conventions` skill** — it covers the agentskills.io spec, the frontmatter policy, and the authoring playbook.

## Testing rules
- Always run `chezmoi diff` before applying to verify expected output.
- After `chezmoi re-encrypt`, run `chezmoi apply --dry-run` first to catch decryption failures.
- After a change under `dot_shell/helper/`, run the stdlib test suites and the linter:
  - `python3 dot_shell/helper/test_shellx.py`
  - `python3 dot_shell/helper/test_embedding_dimensions_proxy.py`
  - `ruff check dot_shell/helper/`

## Boundaries
### ✅ Always
- Load the `chezmoi` skill before editing any template file
- Validate chezmoi behavior against `.help/chezmoi-docs/` or `.help/QUIRKS.md`
- Run `bash .help/fetch_current_docs.sh` if `.help/chezmoi-docs/` is missing
- After a refactor that does not change the source directory layout, run `git status --short`, stage, and commit the working tree before ending the session. If the refactor changes the layout, ask first and do not commit.
- **Put a global rule or skill in `dot_agents/`.** The repo-root `.agents/` tree is project scope and never deploys to `$HOME`. `chezmoi add ~/.agents/rules/x.md` lands in `dot_agents/exact_rules/`. `chezmoi add ~/.agents/skills/x/SKILL.md` lands in `dot_agents/skills/`. Both reach `$HOME`. Edit `dot_agents/` by hand so the source tree shows the full global set.
- **Never place a file in `~/.agents/rules/` or `~/.agents/rules.opencode/` by hand.** `dot_agents/exact_rules/` and `dot_agents/exact_rules.opencode/` carry the `exact_` attribute, so `chezmoi apply` deletes every file there that chezmoi does not manage. `dot_agents/skills/` has no such attribute.
- **Put a project skill in `.agents/skills/<name>/SKILL.md` and a global skill in `dot_agents/skills/<name>/SKILL.md`.** Both are cross-client discovery paths: OpenCode, Codex, Cursor, Gemini CLI, Zed, goose, Amp, Warp and GitHub Copilot read them. Claude Code does not, and neither does the Copilot VS Code harness. Do not copy a shared skill into a per-harness directory. A skill that names one harness's tool or its own frontmatter belongs in that harness's own skills directory, such as `dot_config/opencode/skills/` for `~/.config/opencode/skills/`. Add `metadata.opencode/autoinvoke: false` when the skill must load only on an explicit request.
- **Put a rule that names one harness's tool in that harness's own rule tree.** A shared rule in `dot_agents/exact_rules/` reaches every harness, so it must not depend on a tool that only one harness has. For OpenCode that means `dot_agents/exact_rules.opencode/` or `dot_config/opencode/rules/`. Load the per-harness file with that harness's own `instructions` glob in `dot_config/<vendor>/private_*.jsonc`.

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
- **shellx design and limits** (crypto, JSONC format, export and import, threat model): `dot_shell/helper/.help/` (source-only)
- **Embedding dimensions proxy deployment** (Linux systemd, macOS launchd, client config, multi-OS templating notes): `docs/how-to/embedding-dimensions-proxy-deployment.md`
- **macOS host brief** (what the 2026-11-03 portability change did, what the macOS host receives, and the open items that still assume Linux): `docs/reports/2026-11-03-macos-host-portability-brief.md`
- **AFT embedding findings and measurements**: `docs/reports/` (open findings to hand to the team) and `.agents/docs/cache/aft-embedding/` (the measurements, harness, and query sets behind them)
- **Subagent fleet case study** (haru/natsu/aki/fuyu/shiki): `docs/agent-case-studies.md` (the fleet itself was retired with Kilo on 2026-10-24, and the reusable lessons live here)
- **Full chezmoi conventions + prefix tables**: `.agents/skills/chezmoi/SKILL.md`
- **Project rules**: `.agents/rules/chezmoi-source-project.md`. OpenCode loads it through the `instructions` glob in `.agents/opencode/opencode.jsonc`. Other harnesses read it only if they add the same glob.
- **AGENTS.md lifecycle** (drafting, README↔AGENTS separation, the vendoring trigger): `dot_agents/skills/project-context/SKILL.md` (deployed to `~/.agents/skills/project-context/`)
- **Knowledge cache convention + required `README.md` index**: `.agents/docs/cache/README.md` (full spec: `dot_agents/skills/project-context/references/knowledge-cache.md`)
- **Canonical on-disk project layout** (`.agents/`, `.tmp/` subroles, knowledge cache, vendor unification): `dot_agents/skills/project-layout/SKILL.md` (deployed to `~/.agents/skills/project-layout/`)
- **Local chezmoi/sprig documentation**: `.help/README.md`, `.help/DOCS_MAP.md`, `.help/QUIRKS.md`
- **Shared rules** (web-verification, project-context, local-first, …): `dot_agents/exact_rules/` (deployed to `~/.agents/rules/`)
- **Personal rules** (sudo-ask, ssh-read-allowlist, …): `dot_agents/rules.personal.d/` (deployed to `~/.agents/rules.personal.d/`)
- **SSH keys, gpg-agent, and live output over ssh**: `dot_agents/skills/ssh/SKILL.md` (deployed to `~/.agents/skills/ssh/`)
- **Harness-specific rules (OpenCode only)**: `dot_agents/exact_rules.opencode/` (deployed to `~/.agents/rules.opencode/`) and `dot_config/opencode/rules/` (deployed to `~/.config/opencode/rules/`), both loaded by the `instructions` glob in `dot_config/opencode/private_opencode.jsonc`
