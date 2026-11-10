# AGENTS.md

## Purpose
Personal dotfiles managed with Chezmoi v2.70.4+, age encryption for secrets, Zsh with zgenom/p10k. The repo also carries the global agent rules, skills and harness configs that deploy to `~/.agents/` and `~/.config/`.

## Stack
- **Config**: chezmoi v2.70.4+, `.chezmoi.yaml.tmpl` (age encryption, auto key discovery)
- **Encryption**: age for files, gpg for age-key backups
- **Secrets**: `shellx` in `dot_shell/helper/` (Python 3 stdlib, no pip/venv). It uses scrypt or HMAC-SHA512 key derivation, ChaCha20, and an HMAC-BLAKE2b tag. The master key renders to `~/.local/share/shellx/master.key` (0600).
- **Shell**: zsh, zgenom (plugin manager), powerlevel10k (prompt)
- **Embeddings**: local dimensions proxy in `dot_shell/helper/`, systemd unit in `dot_config/systemd/user/`, and a macOS launchd template in `Library/LaunchAgents/`
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

## Working with other agents
More than one agent works on this repo. The global rules and skills reach nine harnesses. The harness spawns `general` and `explore` subagents. This repo is the source of truth for more than one machine. Each agent has its own context window, so a fact that lives in one agent's head is lost.

- **Write it down.** When you learn a fact the next agent needs and the repo does not carry it, write it before the session ends.
- **A file is the source of truth. Memory is a pointer.** Harness memory does not travel in git, so an agent on a fresh clone never sees it. Put the fact in a file, and let the memory hold the path.
- **Pick the tree by scope.** A reusable fact from web research goes in `.agents/docs/cache/<topic>/`, and the index there is updated. A project note goes in `.agents/docs/`, one topic per file. A rule that every project needs goes in `dot_agents/`. A fact that belongs to this project alone never goes in `dot_agents/`, because that tree deploys to `$HOME`.
- **Carry the evidence.** A written fact names the file, the command, or the URL that proves it.

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
- **Put a rule that names one harness's tool in that harness's own rule tree.** A shared rule in `dot_agents/exact_rules/` reaches every harness, so it must not depend on a tool that only one harness has. For OpenCode that means `dot_agents/exact_rules.opencode/` or `dot_config/opencode/rules/`. Load the per-harness file with that harness's own `instructions` glob in `dot_config/<vendor>/opencode.jsonc`.

### ⚠️ Ask first
- Adding new encryption keys (triggers `chezmoi re-encrypt` across all files)
- Changes to `.chezmoiignore` or `.chezmoidata.yaml`
- Structural changes to the source directory layout

### 🚫 Never
- **Never run `chezmoi apply` in this repository.** It wrote the source tree into the live home on 2026-11-09 and destroyed host-specific state: `docs/post-mortem/2026-11-09-sandbox-apply-wrote-to-real-home.md`. Write a managed target from `chezmoi cat <absolute-target-path>` into a temp file in the same directory, then rename the temp file over the target. The rename replaces a symlink instead of following it, so a symlinked target is not truncated. `chezmoi diff` proves the target state.
- Read or include content from encrypted files. The patterns are listed in `.agents/rules/chezmoi-source-project.md`
- Commit plaintext secrets, keys, tokens, or credentials
- Encrypt a file without running `chezmoi re-encrypt` afterwards
- Never modify `.encryption_keys/`. Adding a recipient key rewrites every encrypted file, so run `chezmoi re-encrypt` only after the user approves.
- Put a harness's own config in `.agents/<vendor>/` expecting another harness to read it — only `.agents/skills/` is a shared discovery location

## Pointers
- **`README.md`** — human-facing project overview, features, installation, usage, contributing
- **shellx design and limits** (crypto, JSONC format, export and import, threat model): `dot_shell/helper/.help/` (source-only)
- **Embedding dimensions proxy deployment** (Linux systemd, macOS launchd, client config, multi-OS templating notes): `docs/how-to/embedding-dimensions-proxy-deployment.md`
- **OpenCode TUI GPU load in Zed** (the streaming-driver measurement, why the fps lever does not exist, and the ranked workarounds): `docs/reports/2026-11-07-opencode-tui-gpu-load-in-zed.md`
- **Hostname router and the shell dispatchers** (the `.chezmoitemplates` host profile table, the `~/.zshenv` → `~/.shell/.zshenv` secret dispatcher, `~/.shell/bashrc.local`, and the PATH owner `~/.shell/env/path.sh`): `docs/plans/2026-11-09-macos-host-router-and-upstream-apply/`
- **macOS host** (the 2026-11-03 portability change, what the macOS host receives, and the open items that still assume Linux): `docs/reports/2026-11-03-macos-host-portability.md` for human readers, `.agents/docs/macos-host-handoff.md` for an agent that works on the macOS host
- **macOS apply audit** (the six blockers on the macOS work laptop, the decisions taken on each, and the backup tooling): `docs/reports/2026-11-03-macos-apply-audit/` for human readers, `.agents/docs/macos-apply-blockers.md`, `.agents/docs/macos-apply-target-state.md`, `.agents/docs/macos-apply-caveats.md` and `.agents/docs/macos-apply-fixed.md` for an agent
- **AFT embedding findings and measurements**: `docs/reports/` (open findings to hand to the team) and `.agents/docs/cache/aft-embedding/` (the measurements, harness, and query sets behind them)
- **Agent design case studies** (haru, natsu, aki, fuyu, shiki, reki, assist-only): `docs/agent-case-studies.md` (the fleet was retired with Kilo on 2026-10-24, and the doc harvests the transferable rules)
- **Full chezmoi conventions + prefix tables**: `.agents/skills/chezmoi/SKILL.md`
- **Project rules**: `.agents/rules/chezmoi-source-project.md`. OpenCode loads it through the `instructions` glob in `.agents/opencode/opencode.jsonc`. Other harnesses read it only if they add the same glob.
- **Agent-only notes** (context that only an agent needs, one file per topic, no date prefix, no index): `.agents/docs/`
- **Knowledge cache convention + required `README.md` index**: `.agents/docs/cache/README.md` (full spec: `dot_agents/skills/project-context/references/knowledge-cache.md`)
- **Canonical on-disk project layout** (`.agents/`, `.tmp/` subroles, knowledge cache, vendor unification): `dot_agents/skills/project-layout/SKILL.md` (deployed to `~/.agents/skills/project-layout/`)
- **Local chezmoi/sprig documentation**: `.help/DOCS_MAP.md` (which doc answers which question), `.help/QUIRKS.md` (observed template quirks)
- **Personal rules** (sudo-ask, ssh-read-allowlist, …): `dot_agents/rules.personal.d/` (deployed to `~/.agents/rules.personal.d/`)
